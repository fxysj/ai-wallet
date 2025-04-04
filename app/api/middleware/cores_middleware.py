from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.request_logger import RequestLoggingMiddleware


def setup_cors_middleware(app: FastAPI):
    # 定义允许的跨域来源列表
    # 这里可以根据实际需求添加更多的域名，例如 ["http://example.com", "https://another-example.com"]
    # 如果要允许所有来源，可以使用 ["*"]，但这在生产环境中可能存在安全风险
    origins = [
       "*"
    ]

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 允许的跨域来源列表
        allow_credentials=True,  # 允许携带凭证（如 cookies）
        allow_methods=["*"],  # 允许的 HTTP 请求方法，* 表示允许所有方法
        allow_headers=["*"],  # 允许的 HTTP 请求头，* 表示允许所有头
    )
    return app

