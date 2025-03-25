#深度账号交易分析
from app.agents.schemas import AgentState
async def analysis_task(state: AgentState) -> AgentState:
    return state.copy(update={"task_result": "analysis_task 处理完成", "is_signed": True})