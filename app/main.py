# FastAPI 入口
from fastapi import FastAPI
from app.api.chat_api import router as chat_router
from app.agents.lib.session.sessionManager import dict_manager
from app.api.middleware.cores_middleware import setup_cors_middleware
from fastapi import FastAPI, Request

from app.api.middleware.logging_middleware import setup_logging

app = FastAPI(title="区块链智能助手 Pro",
              description="提供转账、查询余额等功能",
              version="1.0.0")
#设置跨域
app = setup_cors_middleware(app)
#设置日志
# 设置日志
# app = setup_logging(app)
# 注册 API
app.include_router(chat_router, prefix="/api/v1")



# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
