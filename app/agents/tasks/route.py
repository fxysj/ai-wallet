# 路由智能体进行转换
from app.agents.schemas import AgentState


def route_task(state: AgentState) -> str:
    print("路由匹配")
    return str(state.detected_intent.value)


# 判断是否结束的标志
def mutilisEnd(state: AgentState) -> str:
    print("多轮兑换路由匹配===================")
    print(state)
    if state.isEnd:
        return "end"
    else:
        return "intent_parser"
