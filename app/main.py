# FastAPI 入口
import uvicorn
from app.api.chat_api import router as chat_router
from app.api.middleware.cores_middleware import setup_cors_middleware
from fastapi import FastAPI
from app.db.database import engine
from app.db.models import Base

app = FastAPI(title="区块链智能助手 Pro",
              description="提供转账、查询余额等功能",
              version="1.0.0")
#设置跨域
app = setup_cors_middleware(app)
# 注册 API
app.include_router(chat_router, prefix="/api/v1")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 启动服务
if __name__ == "__main__":
    #asyncio.run(init_db())  # 确保数据库初始化
    uvicorn.run(app, host="0.0.0.0", port=8000,reload=True)
