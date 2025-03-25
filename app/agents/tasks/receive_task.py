# 处理收款任务
from app.agents.schemas import AgentState
from app.agents.tools import GetWrapResponse


async def receive_task(state: AgentState) -> AgentState:
    # 先返回响应
    response = GetWrapResponse(
        data={},
        history=state.history,
        missfield="",
        detected_intent=state.detected_intent.value,
        system_response="",
        is_completed=False,
        description="",
    )
    return state.copy(update={"task_result": response})
