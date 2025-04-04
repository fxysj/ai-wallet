from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 替换你的 MySQL 连接信息
DATABASE_URL = "mysql+aiomysql://root:root@127.0.0.1:3306/ai_wallet_db"

# 创建异步数据库引擎
engine = create_async_engine(DATABASE_URL, echo=True)
print(engine)

# 创建异步 session 工厂
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
