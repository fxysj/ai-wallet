#路由智能体进行转换
from app.agents.schemas import AgentState
def route_task(state: AgentState) -> str:
    print("路由匹配")
    return str(state.detected_intent.value)