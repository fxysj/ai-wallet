from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import StreamingResponse

from .exceptions import BusinessException, ModelOutputException
from langchain_core.exceptions import OutputParserException

from ...agents.lib.aiNodeJsSDk.tools.AgentStateResponseWrape import stream_text_agent_state_transfor
from ...agents.response.Response import SystemResponse


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message="Please be patient for a moment. Your request has been processed and is currently being processed",
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor(
        "Please be patient for a moment. Your request has been processed and is currently being processed",
        response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def business_exception_handler(request: Request, exc: BusinessException):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message="Please be patient for a moment. Your request has been processed and is currently being processed",
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor(
        "Please be patient for a moment. Your request has been processed and is currently being processed",
        response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def model_output_exception_handler(request: Request, exc: ModelOutputException):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message="Please be patient for a moment. Your request has been processed and is currently being processed",
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor(
        "Please be patient for a moment. Your request has been processed and is currently being processed",
        response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def output_parser_exception_handler(request: Request, exc: OutputParserException):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message="Please be patient for a moment. Your request has been processed and is currently being processed",
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor(
        "Please be patient for a moment. Your request has been processed and is currently being processed",
        response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def global_exception_handler(request: Request, exc: Exception):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message="Please be patient for a moment. Your request has been processed and is currently being processed",
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor("Please be patient for a moment. Your request has been processed and is currently being processed", response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response
