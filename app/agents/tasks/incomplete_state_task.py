#账号是否填充完成
from app.agents.schemas import AgentState
from app.agents.tools import FormGenerator
from app.agents.tools import  ConversationManager
async def handle_incomplete(state: AgentState) -> AgentState:
    form_template = FormGenerator.get_form_template(state.detected_intent)
    system_message = {
        "role": "assistant",
        "content": f"请按照以下模板填写信息：\n{form_template}"
    }
    state = ConversationManager.update_history(state, system_message)

    return state.copy(update={
        "task_result": f"请补充以下信息: {state.task_result.split(': ')[1]}",
        "is_signed": False
    })