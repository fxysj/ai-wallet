# 处理购买任务
from app.agents.schemas import AgentState

async def buy_task(state: AgentState) -> AgentState:
    return state.copy(update={"task_result": "buy_task 处理完成", "is_signed": True})
