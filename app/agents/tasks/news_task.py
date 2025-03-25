#新闻资讯任务处理器
from app.agents.schemas import AgentState
async def news_task(state: AgentState) -> AgentState:
    return state.copy(update={"task_result": "news_task 处理完成", "is_signed": True})