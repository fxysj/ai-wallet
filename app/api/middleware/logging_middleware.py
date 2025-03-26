import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time


class SingletonLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(pathname)s:%(lineno)d | '
            'Path: %(path)s | Method: %(method)s | Status: %(status_code)s | '
            'Duration: %(duration)dms | Message: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


def setup_logging(app: FastAPI):
    logger = SingletonLogger().logger

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        logger.info(
            "Incoming request",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": None,
                "duration": 0
            }
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                "Request processing failed",
                exc_info=e,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": 500,
                    "duration": int((time.time() - start_time) * 1000)
                }
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

        duration = int((time.time() - start_time) * 1000)

        logger.info(
            "Request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration": duration
            }
        )

        return response

    return app