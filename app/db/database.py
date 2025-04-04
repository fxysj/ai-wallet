from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
# 替换你的 MySQL 连接信息
DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.REDIS_HOST}/{settings.MYSQL_DATABASE}"

# 创建异步数据库引擎
engine = create_async_engine(DATABASE_URL, echo=True)
print(engine)

# 创建异步 session 工厂
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
