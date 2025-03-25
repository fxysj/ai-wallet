#深度搜索分析
from app.agents.schemas import AgentState
async def research_task(state: AgentState) -> AgentState:
    return state.copy(update={"task_result": "research_task 处理完成", "is_signed": True})