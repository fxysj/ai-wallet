import asyncio
import json
import time
from typing import Dict, Any, Optional
from pymongo import MongoClient
from loguru import logger
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt
from pydantic import BaseModel, Field
from langchain_core.agents import AgentFinish
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.config import settings

# ==================== 配置常量 ====================
DEFAULT_MONGO_URI = "mongodb://localhost:27017"
MAX_RETRIES = 3


def safe_int(val):
    return val if isinstance(val, int) and val is not None else 0

# ==================== 工具定义 ====================
class WeatherToolInput(BaseModel):
    location: str = Field(..., description="城市名称，如 'Beijing'")
    date: Optional[str] = Field(None, description="日期，格式YYYY-MM-DD，可选")

@tool("weather_tool", args_schema=WeatherToolInput)
async def weather_tool(location: str, date: Optional[str] = None) -> str:
    """查询指定城市的天气信息"""
    try:
        await asyncio.sleep(0.2)  # 模拟网络延迟

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

        city_weather = weather_db.get(location, weather_db["default"])
        if isinstance(city_weather, dict):
            return city_weather.get(date, city_weather["default"]) if date else city_weather["default"]
        return city_weather

    except Exception as e:
        logger.error(f"[WeatherTool] 查询失败 - {location}: {e}")
        return f"无法获取{location}的天气信息"

# ==================== 回调处理器 ====================
class RobustAsyncCallbackHandler(AsyncCallbackHandler):
    def __init__(self, storage_backend: Optional[Any] = None):
        self.state: Dict[str, Any] = {
            "reasoning_trace": [],
            "token_usage": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
        }
        self.storage = storage_backend or FileStorage()
        self.lock = asyncio.Lock()

    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        async with self.lock:
            try:
                usage = getattr(response, "llm_output", {}).get("token_usage", {})
                self.state["token_usage"]["prompt_tokens"] += usage.get("prompt_tokens", 0)
                self.state["token_usage"]["completion_tokens"] += usage.get("completion_tokens", 0)
                self.state["token_usage"]["total_tokens"] += usage.get("total_tokens", 0)
                await self._safe_save()
            except Exception as e:
                logger.warning(f"[Callback] Token记录失败: {e}")

    async def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        async with self.lock:
            try:
                self.state["reasoning_trace"].append({
                    "timestamp": time.time(),
                    "type": "action",
                    "thought": getattr(action, "log", "No log").strip(),
                    "action": kwargs.get("tool_name", ""),
                    "action_input": str(kwargs.get("tool_input", ""))
                })
                await self._safe_save()
            except Exception as e:
                logger.warning(f"[Callback] 代理动作记录失败: {e}")

    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        async with self.lock:
            try:
                usage = getattr(response, "llm_output", {}).get("token_usage", {})
                self.state["token_usage"]["prompt_tokens"] += safe_int(usage.get("prompt_tokens"))
                self.state["token_usage"]["completion_tokens"] += safe_int(usage.get("completion_tokens"))
                self.state["token_usage"]["total_tokens"] += safe_int(usage.get("total_tokens"))
                await self._safe_save()
            except Exception as e:
                logger.warning(f"[Callback] Token记录失败: {e}")

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        async with self.lock:
            try:
                self.state["reasoning_trace"].append({
                    "timestamp": time.time(),
                    "type": "finish",
                    "thought": getattr(finish, "log", "No log").strip(),
                    "final_answer": finish.return_values.get("output", ""),
                    "token_usage": self.state["token_usage"].copy()
                })
                await self._safe_save()
            except Exception as e:
                logger.warning(f"[Callback] 代理完成记录失败: {e}")

    async def _safe_save(self):
        try:
            await self.storage.save(self.state.copy())
        except Exception as e:
            logger.warning(f"[Callback] 状态保存失败: {e}")

# ==================== 存储后端实现 ====================
class FileStorage:
    @retry(stop=stop_after_attempt(MAX_RETRIES))
    async def save(self, data: Dict):
        try:
            with open("reasoning_trace.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[FileStorage] 保存失败: {e}")
            raise

class MongoDBStorage:
    def __init__(self, uri: str = DEFAULT_MONGO_URI, db_name: str = "ai_traces"):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.collection = self.db["traces"]
            self.client.server_info()  # 测试连接
        except Exception as e:
            logger.error(f"[MongoDB] 初始化失败: {e}")
            raise

    @retry(stop=stop_after_attempt(MAX_RETRIES))
    async def save(self, data: Dict):
        try:
            data_copy = data.copy()
            data_copy["_timestamp"] = time.time()
            self.collection.insert_one(data_copy)
        except Exception as e:
            logger.error(f"[MongoDB] 保存失败: {e}")
            raise

# ==================== LLM工厂类 ====================
class LLMFactory:
    @staticmethod
    def getDefaultOPENAI():
        return ChatOpenAI(temperature=0,base_url=settings.OPENAI_API_BASE_URL,api_key=settings.OPENAI_API_KEY)

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
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[callback_handler],
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        verbose=True
    )

    return executor, callback_handler

# ==================== 主执行逻辑 ====================
async def main():
    try:
        logger.info("🎯 初始化代理中...")
        agent_executor, callback_handler = initialize_agent()

        questions = [
            "What's the weather like in Beijing tomorrow?",
            "How about Shanghai today?",
            "Tell me the weather conditions in New York on 2023-11-15"
        ]

        for question in questions:
            logger.info(f"💬 处理问题: {question}")
            try:
                response = await agent_executor.ainvoke({"input": question})
                logger.success(f"✅ 结果: {response['output']}")
            except Exception as e:
                logger.error(f"❌ 错误处理问题 [{question}]: {e}")

        await callback_handler.storage.save(callback_handler.state)
        logger.info("📦 追踪数据保存完成")

    except Exception as e:
        logger.critical(f"💥 主程序异常退出: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
