# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import MYSQL_CONFIG

# 从环境变量获取 MySQL 配置（推荐），或者你可以直接写死测试用
MYSQL_USER = MYSQL_CONFIG["user"]
MYSQL_PASSWORD = MYSQL_CONFIG["password"]
MYSQL_HOST = MYSQL_CONFIG["host"]
MYSQL_PORT = MYSQL_CONFIG["port"]
MYSQL_DB = MYSQL_CONFIG["database"]

# ✅ 构造标准 MySQL 数据库 URL（使用 aiomysql 驱动）
DATABASE_URL = (
    f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

print("✅ 使用数据库连接:", DATABASE_URL)

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# 创建异步 Session 工厂
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# ✅ 获取异步 DB Session（可用于 Depends）
async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# ✅ 所有模型继承此 Base
Base = declarative_base()
