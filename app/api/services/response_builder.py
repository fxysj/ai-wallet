from json import JSONDecodeError

from fastapi.responses import StreamingResponse

from app.agents.lib.aiNodeJsSDk.tools.AgentStateResponseWrape import stream_text_agent_state_transfor
from app.agents.response.Response import SystemResponse
from app.agents.tools import get_nested_description
from app.api.services.prompt_action_service import handle_chain_result


def build_success_response(result):
    prom_action = handle_chain_result(result)

    response_data = SystemResponse.success(
        prompt_next_action=prom_action,
        data=result.get("result", {}),
        message="ok",
        content=get_nested_description(result)
    )

    res = stream_text_agent_state_transfor(get_nested_description(result), response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response

def build_error_response(error):
    import traceback
    traceback.print_exc()

    message = "请稍后重试" if not isinstance(error, JSONDecodeError) else "Please try again!"
    response_data = SystemResponse.errorWrap(
        data={},
        message=message,
        prompt_next_action=[],
    )
    res = stream_text_agent_state_transfor(message, response_data.to_dict())
    response = StreamingResponse(res, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response
