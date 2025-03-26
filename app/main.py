# FastAPI 入口
import logging

from fastapi import FastAPI
from app.api.chat_api import router as chat_router
from app.agents.lib.session.sessionManager import dict_manager
from app.api.middleware.cores_middleware import setup_cors_middleware


app = FastAPI(title="区块链智能助手 Pro",
              description="提供转账、查询余额等功能",
              version="1.0.0")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
#设置中间件
app = setup_cors_middleware(app)
# 注册 API
app.include_router(chat_router, prefix="/api/v1")

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
