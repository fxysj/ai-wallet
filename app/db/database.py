# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 拼接 SQLite 路径
db_path = os.path.join(BASE_DIR, "agent_state.db")

# ✅ 构造标准 SQLite 数据库 URL（无需判断平台）
DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

print("✅ 使用数据库路径:", db_path)

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
