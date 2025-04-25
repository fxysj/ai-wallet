import asyncio
import json

from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import StreamingResponse

from app.api.exceptions.exceptions import BusinessException, ModelOutputException
from langchain_core.exceptions import OutputParserException

from app.agents.lib.aiNodeJsSDk.tools.AgentStateResponseWrape import stream_text_agent_state_transfor
from app.agents.response.Response import SystemResponse

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
    res = stream_text_agent_state_transfor(message, response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
    #message = load_error_message()
    return create_error_response(message)

async def business_exception_handler(request: Request, exc: BusinessException):
    #message = load_error_message()
    message = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
    return create_error_response(message)

async def model_output_exception_handler(request: Request, exc: ModelOutputException):
    #message = load_error_message()
    message = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
    return create_error_response(message)

async def output_parser_exception_handler(request: Request, exc: OutputParserException):
    #message = load_error_message()
    message = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
    return create_error_response(message)

async def global_exception_handler(request: Request, exc: Exception):
    #message = load_error_message()
    message = "Sorry, I ran into a bit of an issue while processing your request. I've logged the details, so feel free to try again in a moment!"
    return create_error_response(message)

