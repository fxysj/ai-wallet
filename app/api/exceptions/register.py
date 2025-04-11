from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from .handlers import (
    http_exception_handler,
    business_exception_handler,
    model_output_exception_handler,
    output_parser_exception_handler,
    global_exception_handler
)
from .exceptions import BusinessException, ModelOutputException
from langchain_core.exceptions import OutputParserException

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(ModelOutputException, model_output_exception_handler)
    app.add_exception_handler(OutputParserException, output_parser_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
