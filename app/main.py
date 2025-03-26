# FastAPI 入口
import logging
import time

from fastapi import FastAPI
from app.api.chat_api import router as chat_router
from app.agents.lib.session.sessionManager import dict_manager
from app.api.middleware.cores_middleware import setup_cors_middleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


app = FastAPI(title="区块链智能助手 Pro",
              description="提供转账、查询余额等功能",
              version="1.0.0")

# 创建日志记录器
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
#
# # 创建文件处理器
# file_handler = logging.FileHandler('app.log')
# file_handler.setLevel(logging.INFO)
#
# # 创建控制台处理器
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
#
# # 定义日志格式
# # 定义全面日志格式（包含请求元数据）
# formatter = logging.Formatter(
#     '%(asctime)s | %(levelname)s | %(name)s | %(pathname)s:%(lineno)d | '
#     'Path: %(path)s | Method: %(method)s | Status: %(status_code)s | '
#     'Duration: %(duration)dms | Message: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)
# logger.info("Received a request to the root endpoint")
#设置中间件
app = setup_cors_middleware(app)
# 注册 API
app.include_router(chat_router, prefix="/api/v1")


# 全局请求日志中间件
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()
#
#     # 记录请求信息
#     logger.info(
#         "Incoming request",
#         extra={
#             "path": request.url.path,
#             "method": request.method,
#             "status_code": None,
#             "duration": 0
#         }
#     )
#
#     try:
#         response = await call_next(request)
#     except Exception as e:
#         # 记录异常信息
#         logger.error(
#             "Request processing failed",
#             exc_info=e,
#             extra={
#                 "path": request.url.path,
#                 "method": request.method,
#                 "status_code": 500,
#                 "duration": int((time.time() - start_time) * 1000)
#             }
#         )
#         return JSONResponse(
#             status_code=500,
#             content={"detail": "Internal server error"}
#         )
#
#     # 计算响应时间
#     duration = int((time.time() - start_time) * 1000)
#
#     # 记录响应信息
#     logger.info(
#         "Request completed",
#         extra={
#             "path": request.url.path,
#             "method": request.method,
#             "status_code": response.status_code,
#             "duration": duration
#         }
#     )
#
#     return response
# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
