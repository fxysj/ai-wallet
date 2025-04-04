import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RequestLog
from app.db.database import async_session_factory

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """中间件：异步记录请求和响应到 MySQL"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        session: AsyncSession = async_session_factory()

        # 解析请求数据
        try:
            body = await request.body()
            request_data = body.decode("utf-8") if body else "{}"
        except Exception:
            request_data = "{}"

        # 处理请求
        response: Response = await call_next(request)

        # 解析响应数据
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        response_data = response_body.decode("utf-8") if response_body else "{}"

        # 计算请求耗时
        duration = round(time.time() - start_time, 6)

        # 异步保存日志
        await self.save_log(session, request, response, request_data, response_data, duration)

        return Response(content=response_body, status_code=response.status_code, headers=dict(response.headers))

    async def save_log(self, session, request, response, request_data, response_data, duration):
        """异步存储请求和响应日志"""
        log_entry = RequestLog(
            method=request.method,
            url=str(request.url),
            headers=json.dumps(dict(request.headers)),
            request_body=request_data,
            response_body=response_data,
            status_code=response.status_code,
            duration=duration,
            timestamp=int(time.time()),
        )
        async with session.begin():
            session.add(log_entry)
