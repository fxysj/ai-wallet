from app.agents.schemas import AgentState, Intention
from app.agents.utils import chain_data_util
from app.config import settings


def build_initial_state(request_data, session_id, user_input_object, history, messages):
    return AgentState(
        user_input=user_input_object.content,
        attached_data=user_input_object.data,
        session_id=session_id,
        history=history,
        chain_data=chain_data_util.DEFAULT_CHAIN_DATA,
        messages=messages,
        langguage=settings.LanGuage,
        isAsync=settings.ISLangGuageAynsNIS,
        detected_intent=Intention.unclear,
        thinking_info="模型正在进行思考..."
    )
