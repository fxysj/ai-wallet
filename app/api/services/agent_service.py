from fastapi import Request
from json import JSONDecodeError
from pydantic import ValidationError
import logging

from app.api.models.state_models import build_initial_state
from app.api.services.response_builder import build_success_response, build_error_response
from app.api.services.session_service import init_session, update_session_history
from app.utuls.Messages import Session
from app.api.chat_api import  app

logger = logging.getLogger(__name__)

async def analyze_request_logic(request: Request):
    try:
        request_data = await request.json()
        session_id = request_data.get("session_id") or request_data.get("id")
        messages = request_data.get("messages")

        if not session_id:
            from response_builder import SystemResponse
            return SystemResponse.error_with_message(message="请先进行授权登录钱包")

        session = init_session(session_id)
        user_input_object = Session.get_last_user_message(request_data)
        history = Session.get_recent_history(request_data, 10)

        initial_state = build_initial_state(request_data, session_id, user_input_object, history, messages)
        result = await app.ainvoke(initial_state)
        request.state.agent_state = result

        update_session_history(session, user_input_object, result, session_id)
        return build_success_response(result)

    except (KeyError, ValidationError, ValueError, JSONDecodeError, Exception) as e:
        logger.error(f"处理失败: {str(e)}")
        return build_error_response(e)
