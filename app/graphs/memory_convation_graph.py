from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage

from app.agents.memory.MemoryPool import MemoryPool


# 对话状态类型
class GraphState(TypedDict):
    user_id:str
    user_input: str
    messages: Annotated[List[BaseMessage], "All messages"]



# agent 节点：处理用户输入并返回模型回复
def agent_node(state: GraphState) -> GraphState:
    user_input = state["user_input"]

    memory = MemoryPool.get(user_id=state["user_id"],url="redis://localhost:6380/1")

    # 用 Memory 封装类进行问答
    response = memory.ask(user_input)

    # 获取完整历史
    history = memory.get_all_messages()

    return {
        "user_input": user_input,
        "messages": history
    }

# 构建 LangGraph 对话图
builder = StateGraph(GraphState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.set_finish_point("agent")

graph = builder.compile()

# user_id 可来自登录系统、钱包地址等
user_id = "user_abc_001"

# 第 1 轮
state = graph.invoke({
    "user_id": user_id,
    "user_input": "你好，帮我推荐一个适合亲子旅游的城市？",
    "messages": []  # 初始化为空列表
})
print(state["messages"][-1].content)

# 第 2 轮
state = graph.invoke({
    "user_id": user_id,
    "user_input": "这个城市有哪些必去的景点？",
    "messages": state["messages"]  # 上一轮返回的消息
})
print(state["messages"][-1].content)

# 第 3 轮
state = graph.invoke({
    "user_id": user_id,
    "user_input": "两天一夜的话怎么安排？",
    "messages": state["messages"]
})
print(state["messages"][-1].content)