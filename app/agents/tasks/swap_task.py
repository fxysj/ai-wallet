# 处理兑换任务
from app.agents.schemas import AgentState
async def swap_task(state: AgentState) -> AgentState:
    return state.copy(update={"task_result": "swap_task 处理完成", "is_signed": True})
