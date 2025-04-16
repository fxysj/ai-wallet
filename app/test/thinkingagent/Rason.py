import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from loguru import logger
from langgraph import prebuilt
from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from pydantic import BaseModel, Field
from app.config import settings

# ==================== 天气工具函数 ====================
class WeatherToolInput(BaseModel):
    """天气查询工具的输入参数"""
    location: str = Field(description="城市名称，如'Beijing'")
    date: Optional[str] = Field(default=None, description="日期，格式YYYY-MM-DD")


class WeatherTool:
    """模拟天气查询工具"""

    name = "weather_tool"
    description = "查询指定城市和日期的天气情况"
    args_schema = WeatherToolInput

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(Exception))
    async def _arun(self, location: str, date: Optional[str] = None) -> str:
        """异步执行天气查询"""
        try:
            # 这里模拟API调用，实际应用中替换为真实天气API
            await asyncio.sleep(0.5)  # 模拟网络延迟

            # 模拟天气数据
            weather_data = {
                "Beijing": {
                    "2023-11-15": "Sunny, 15°C, 湿度30%, 西北风3级",
                    "2023-11-16": "Cloudy, 12°C, 湿度45%, 东风2级",
                    "default": "Partly cloudy, 12°C, 湿度40%, 微风"
                },
                "Shanghai": {
                    "2023-11-15": "Rainy, 18°C, 湿度85%, 东南风4级",
                    "2023-11-16": "Overcast, 20°C, 湿度75%, 东风3级",
                    "default": "Cloudy, 20°C, 湿度70%, 东南风2级"
                },
                "New York": {
                    "2023-11-15": "Snow, -2°C, 湿度60%, 北风5级",
                    "2023-11-16": "Sunny, 5°C, 湿度50%, 西风3级",
                    "default": "Variable clouds, 8°C, 湿度55%, 西风3级"
                },
                "default": "Sunny, 25°C, 湿度50%, 微风"
            }

            city_data = weather_data.get(location, weather_data["default"])
            if date and isinstance(city_data, dict):
                return city_data.get(date, city_data["default"])
            elif isinstance(city_data, dict):
                return city_data["default"]
            return city_data

        except Exception as e:
            logger.error(f"Weather API error for {location}: {str(e)}")
            return f"无法获取{location}的天气信息: {str(e)}"

    async def run(self, *args, **kwargs):
        """同步接口转异步"""
        return await self._arun(*args, **kwargs)


# ==================== 异步回调处理器 ====================
class AsyncReasoningTraceHandler(AsyncCallbackHandler):
    """支持异步操作的回调处理器"""

    def __init__(self, storage_backend: Optional[Any] = None):
        self.state: Dict[str, List[Dict]] = {"reasoning_trace": []}
        self.storage = storage_backend or FileStorage()  # 默认文件存储
        self.lock = asyncio.Lock()  # 异步锁

    async def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """异步处理代理动作"""
        async with self.lock:
            try:
                thought = action.log.strip() if action and hasattr(action, 'log') else "No log"
                self.state["reasoning_trace"].append({
                    "timestamp": time.time(),
                    "type": "action",
                    "thought": thought,
                    "action": kwargs.get("tool_name", ""),
                    "action_input": str(kwargs.get("tool_input", ""))
                })
                await self._auto_save()
            except Exception as e:
                logger.error(f"Error handling agent action: {str(e)}")
                raise

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """异步处理工具结束"""
        async with self.lock:
            if self.state["reasoning_trace"]:
                try:
                    self.state["reasoning_trace"][-1]["observation"] = output
                    await self._auto_save()
                except KeyError:
                    logger.warning("Missing action entry for tool output")

    async def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """异步处理代理完成"""
        async with self.lock:
            try:
                final_answer = finish.return_values.get('output', '') if hasattr(finish, 'return_values') else ""
                self.state["reasoning_trace"].append({
                    "timestamp": time.time(),
                    "type": "finish",
                    "thought": finish.log.strip() if finish else "No finish log",
                    "final_answer": final_answer
                })
                await self._auto_save()
            except Exception as e:
                logger.error(f"Error handling agent finish: {str(e)}")
                raise

    async def _auto_save(self):
        """自动持久化状态"""
        try:
            await self.storage.save(self.state)
        except Exception as e:
            logger.error(f"Auto-save failed: {str(e)}")


# ==================== 存储实现 ====================
class FileStorage:
    """文件存储实现"""

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(IOError))
    async def save(self, data: Dict):
        try:
            with open("reasoning_trace.json", "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"File save error: {str(e)}")
            raise


class MongoDBStorage:
    """MongoDB存储实现"""

    def __init__(self, uri: str = "mongodb://localhost:27017", db_name: str = "ai_traces"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["traces"]

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(Exception))
    async def save(self, data: Dict):
        try:
            data_copy = data.copy()
            data_copy["_timestamp"] = time.time()
            self.collection.insert_one(data_copy)
        except Exception as e:
            logger.error(f"MongoDB save error: {str(e)}")
            raise


# ==================== LLM工厂类 ====================
class LLMFactory:
    @staticmethod
    def getDefaultOPENAI():
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE_URL,
            streaming=True
        )


# ==================== 结构化日志配置 ====================
logger.add(
    "debug.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    serialize=True,
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8"
)


# ==================== 代理初始化 ====================
@retry(stop=stop_after_attempt(3))
def initialize_agent():
    llm = LLMFactory.getDefaultOPENAI()
    weather_tool = WeatherTool()
    tools = [weather_tool]
    storage = MongoDBStorage()  # 可切换为FileStorage()
    trace_handler = AsyncReasoningTraceHandler(storage)

    return prebuilt.create_react_agent(
        llm=llm,
        tools=tools,
        callbacks=[trace_handler]
    ), trace_handler


# ==================== 单元测试 ====================
# import pytest
# from unittest.mock import MagicMock, patch
#
#
# class TestReasoningTraceHandler:
#     @pytest.mark.asyncio
#     async def test_action_handling(self):
#         handler = AsyncReasoningTraceHandler()
#         mock_action = MagicMock(log="Thinking about weather...")
#
#         await handler.on_agent_action(
#             mock_action,
#             tool_name="weather_tool",
#             tool_input={"location": "Beijing"}
#         )
#
#         assert len(handler.state["reasoning_trace"]) == 1
#         assert handler.state["reasoning_trace"][0]["action"] == "weather_tool"
#         assert "Beijing" in handler.state["reasoning_trace"][0]["action_input"]
#
#     @pytest.mark.asyncio
#     async def test_tool_output(self):
#         handler = AsyncReasoningTraceHandler()
#         await handler.on_agent_action(
#             MagicMock(log="Getting weather data..."),
#             tool_name="weather_tool",
#             tool_input={"location": "Shanghai"}
#         )
#         await handler.on_tool_end("Cloudy, 20°C")
#
#         assert handler.state["reasoning_trace"][0]["observation"] == "Cloudy, 20°C"
#
#     @pytest.mark.asyncio
#     async def test_final_answer(self):
#         handler = AsyncReasoningTraceHandler()
#         mock_finish = MagicMock(
#             log="Final Answer: The weather is sunny",
#             return_values={"output": "The weather in Beijing is sunny, 15°C"}
#         )
#
#         await handler.on_agent_finish(mock_finish)
#
#         assert "sunny" in handler.state["reasoning_trace"][0]["final_answer"]
#
#
# class TestWeatherTool:
#     @pytest.mark.asyncio
#     async def test_weather_tool_basic(self):
#         tool = WeatherTool()
#         result = await tool._arun("Beijing")
#         print(result)
#         assert "°C" in result
#         assert "Beijing" in result or "北京" in result
#
#     @pytest.mark.asyncio
#     async def test_weather_tool_with_date(self):
#         tool = WeatherTool()
#         result = await tool._arun("Shanghai", "2023-11-15")
#         assert "Rainy" in result or "雨" in result
#         assert "18°C" in result
#
#     @pytest.mark.asyncio
#     async def test_weather_tool_unknown_city(self):
#         tool = WeatherTool()
#         result = await tool._arun("UnknownCity")
#         assert "25°C" in result  # 使用默认值


# ==================== 使用示例 ====================
async def main():
    try:
        logger.info("Initializing agent...")
        agent, trace_handler = initialize_agent()

        questions = [
            "What's the weather like in Beijing tomorrow?",
            "How about Shanghai today?",
            "Tell me the weather conditions in New York on 2023-11-15"
        ]

        for question in questions:
            logger.info(f"Processing question: {question}")
            response = await agent.ainvoke({
                "messages": [HumanMessage(content=question)]
            })

            logger.success("Agent Response: {}", response['messages'][-1].content)
            logger.debug("Full Trace: {}", json.dumps(trace_handler.state, indent=2))

        # 手动触发最终保存
        await trace_handler.storage.save(trace_handler.state)
        logger.info("All traces saved successfully")

    except Exception as e:
        logger.critical("Main execution failed: {}", str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())