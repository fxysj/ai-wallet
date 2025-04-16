import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from loguru import logger
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from pydantic import BaseModel, Field
from langchain_core.agents import AgentFinish
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.lib.llm.llm import LLMFactory

# ==================== 配置常量 ====================
DEFAULT_MONGO_URI = "mongodb://localhost:27017"
MAX_RETRIES = 3


# ==================== 天气工具函数 ====================
class WeatherToolInput(BaseModel):
    """天气查询工具的输入参数"""
    location: str = Field(..., description="城市名称，如'Beijing'")
    date: Optional[str] = Field(None, description="可选日期，格式YYYY-MM-DD")


@tool("weather_tool", args_schema=WeatherToolInput)
async def weather_tool(location: str, date: Optional[str] = None) -> str:
    """查询指定城市和日期的天气情况"""
    try:
        await asyncio.sleep(0.2)

        weather_db = {
            "Beijing": {
                "2023-11-15": "Sunny, 15°C, 湿度30%, 西北风3级",
                "2023-11-16": "Cloudy, 12°C, 湿度45%, 东风2级",
                "default": "Partly cloudy, 12°C"
            },
            "Shanghai": {
                "2023-11-15": "Rainy, 18°C, 湿度85%, 东南风4级",
                "2023-11-16": "Overcast, 20°C, 湿度75%, 东风3级",
                "default": "Cloudy, 20°C"
            },
            "default": "Sunny, 25°C"
        }

        city_data = weather_db.get(location, weather_db["default"])
        if isinstance(city_data, dict):
            if date:
                return city_data.get(date, city_data["default"])
            return city_data["default"]
        return city_data

    except Exception as e:
        logger.error(f"天气查询失败 {location}: {e}")
        return f"无法获取{location}的天气信息"


# ==================== 健壮的回调处理器 ====================
class RobustAsyncCallbackHandler(AsyncCallbackHandler):
    def __init__(self, storage_backend: Optional[Any] = None):
        self.state: Dict[str, Any] = {
            "reasoning_trace": [],
            "token_usage": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0
            }
        }
        self.storage = storage_backend or FileStorage()
        self.lock = asyncio.Lock()

    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """安全处理LLM结束事件，即使没有token数据"""
        async with self.lock:
            try:
                usage = {}
                if hasattr(response, "llm_output") and response.llm_output:
                    usage = response.llm_output.get("token_usage", {})

                # 安全更新token计数
                self.state["token_usage"]["prompt_tokens"] += usage.get("prompt_tokens", 0)
                self.state["token_usage"]["completion_tokens"] += usage.get("completion_tokens", 0)
                self.state["token_usage"]["total_tokens"] += max(
                    usage.get("total_tokens", 0),
                    usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))

                await self._safe_save()
            except Exception as e:
                logger.warning(f"处理LLM token使用数据失败: {e}")

    async def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        async with self.lock:
            try:
                entry = {
                    "timestamp": time.time(),
                    "type": "action",
                    "thought": getattr(action, 'log', 'No log').strip(),
                    "action": kwargs.get("tool_name", ""),
                    "action_input": str(kwargs.get("tool_input", ""))
                }
                self.state["reasoning_trace"].append(entry)
                await self._safe_save()
            except Exception as e:
                logger.warning(f"记录代理动作失败: {e}")

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        async with self.lock:
            try:
                if self.state["reasoning_trace"]:
                    self.state["reasoning_trace"][-1]["observation"] = output
                    await self._safe_save()
            except Exception as e:
                logger.warning(f"记录工具输出失败: {e}")

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        async with self.lock:
            try:
                entry = {
                    "timestamp": time.time(),
                    "type": "finish",
                    "thought": getattr(finish, 'log', 'No log').strip(),
                    "final_answer": finish.return_values.get('output', ''),
                    "token_usage": self.state["token_usage"].copy()
                }
                self.state["reasoning_trace"].append(entry)
                await self._safe_save()
            except Exception as e:
                logger.warning(f"记录代理完成失败: {e}")

    async def _safe_save(self):
        """带多重保护的保存方法"""
        try:
            if self.storage:
                await self.storage.save(self.state.copy())
        except Exception as e:
            logger.warning(f"保存状态失败: {e}")


# ==================== 存储实现 ====================
class FileStorage:
    @retry(stop=stop_after_attempt(MAX_RETRIES))
    async def save(self, data: Dict):
        try:
            with open("reasoning_trace.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise


class MongoDBStorage:
    def __init__(self, uri: str = DEFAULT_MONGO_URI, db_name: str = "ai_traces"):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.collection = self.db["traces"]
            self.client.server_info()  # 测试连接
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise

    @retry(stop=stop_after_attempt(MAX_RETRIES))
    async def save(self, data: Dict):
        try:
            data_copy = data.copy()
            data_copy["_timestamp"] = time.time()
            self.collection.insert_one(data_copy)
        except Exception as e:
            logger.error(f"MongoDB保存失败: {e}")
            raise


# ==================== 代理初始化 ====================
def initialize_agent():
    llm = LLMFactory.getDefaultOPENAI()

    tools = [weather_tool]
    storage = MongoDBStorage()
    callback_handler = RobustAsyncCallbackHandler(storage)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Respond to the user's request appropriately."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[callback_handler],
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )

    return agent_executor, callback_handler


# ==================== 主程序 ====================
async def main():
    try:
        logger.info("初始化代理...")
        agent_executor, callback_handler = initialize_agent()

        questions = [
            "What's the weather like in Beijing tomorrow?",
            "How about Shanghai today?",
            "Tell me the weather conditions in New York on 2023-11-15"
        ]

        for question in questions:
            logger.info(f"处理问题: {question}")
            try:
                response = await agent_executor.ainvoke({"input": question})
                logger.success(f"代理响应: {response['output']}")
            except Exception as e:
                logger.error(f"处理问题失败: {question} - {str(e)}")
                continue

        await callback_handler.storage.save(callback_handler.state)
        logger.info("所有追踪记录已保存")

    except Exception as e:
        logger.critical(f"主程序执行失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())