import asyncio
import json

from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import StreamingResponse

from app.api.exceptions.exceptions import BusinessException, ModelOutputException
from langchain_core.exceptions import OutputParserException

from app.agents.lib.aiNodeJsSDk.tools.AgentStateResponseWrape import stream_text_agent_state_transfor, \
    stream_text_agent_state_transfor_annotations
from app.agents.response.Response import SystemResponse
from app.agents.emun.LanguageEnum import get_lang_from_headers, LanguageEnum

exception_en = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
exception_zh_cn = "抱歉，我在处理您的请求时遇到了一些问题。相关信息已记录，您可以稍后再试一次！"
exception_zh_tw = "抱歉，我在處理您的請求時遇到了一些問題。相關資訊已記錄，您可以稍後再試一次！"
# 封装函数
async def get_localized_exception_message(request) -> str:
    language = await get_lang_from_headers(request)

    if language == LanguageEnum.ZH_HANS.value:
        return exception_zh_cn
    elif language == LanguageEnum.ZH_HANT.value:
        return exception_zh_tw
    else:
        return exception_en

# Function to load the message from the configuration file
def load_error_message():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            return config.get("error_message", "Sorry, an error occurred.")
    except Exception as e:
        # If there's an error loading the config, fallback to default message
        return "Sorry, an error occurred."

def create_error_response(message: str):
    response_data = SystemResponse.error(
        data=[],
        content="",
        message=message,
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor_annotations(message, response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = await get_localized_exception_message(request)
    return create_error_response(message)

async def business_exception_handler(request: Request, exc: BusinessException):
    message = await get_localized_exception_message(request)
    return create_error_response(message)

async def model_output_exception_handler(request: Request, exc: ModelOutputException):
    message = await get_localized_exception_message(request)
    return create_error_response(message)

async def output_parser_exception_handler(request: Request, exc: OutputParserException):
    message = await get_localized_exception_message(request)
    return create_error_response(message)




async def global_exception_handler(request: Request, exc: Exception):
    # 从请求头中获取语言
    message = await get_localized_exception_message(request)

    return create_error_response(message)




