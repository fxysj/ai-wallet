from app.agents.schemas import AgentState, Intention


def route_with_retry_check(state: AgentState) -> str:

    # 如果意图不再是 unclear，并且次数未超限，则继续尝试识别对应意图
    print(state.result)
    res = state.result
    print("----intent:")
    intent = res.get("intent")
    print(intent)
    print("----description:")
    description = res.get("description")
    print(description)

    if intent != Intention.unclear.value:
        return intent  # 路由到正确意图处理节点（如 "handle_send"）

    # 超过次数或依然不明确，进入 fail
    return "fail"
