import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# 先加载 .env 文件，确保环境变量可用
load_dotenv()


class Settings(BaseSettings):
    """全局配置类，自动从 .env 读取环境变量"""

    # OpenAI API Key
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_API_BASE_URL: str = Field(..., env="OPENAI_API_BASE_URL")

    # MySQL 数据库配置
    MYSQL_HOST: str = Field(default="localhost", env="MYSQL_HOST")
    MYSQL_USER: str = Field(default="root", env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(default="your-password", env="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(default="chatbot", env="MYSQL_DATABASE")

    # Redis 缓存配置
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")

    LANGSMITH_TRACING: bool = Field(default=True, env="LANGSMITH_TRACING")
    LANGSMITH_ENDPOINT: str = Field(default="", env="LANGSMITH_ENDPOINT")
    LANGSMITH_API_KEY: str = Field(default="", env="LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = Field(default="", env="LANGSMITH_PROJECT")
    SERPAPI_API_KEY: str = Field(default="", env="SERPAPI_API_KEY")

    LanGuage:str = Field(default="en", env="LANGUAGE")

    ISLangGuageAynsNIS:bool =Field(default=False, env="ISLangGuageAynsNIS")

    # 其他缓队列的配置

    class Config:
        env_file = ".env"  # 指定环境变量文件


# 初始化配置
settings = Settings()

# 组织 MySQL 和 Redis 配置
MYSQL_CONFIG = {
    "host": settings.MYSQL_HOST,
    "user": settings.MYSQL_USER,
    "password": settings.MYSQL_PASSWORD,
    "database": settings.MYSQL_DATABASE,
}

REDIS_CONFIG = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "db": settings.REDIS_DB,
}
OPEAI_CONFIG = {
    "KEY": settings.OPENAI_API_KEY,
    "URL": settings.OPENAI_API_BASE_URL
}
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")  # 计算 config.json 的绝对路径


def load_config():
    """加载状态配置文件"""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"配置文件未找到: {CONFIG_PATH}")  # 友好错误提示
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


CONFIG = load_config()  # 加载配置
