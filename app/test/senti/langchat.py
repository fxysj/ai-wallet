#定义一个类型的枚举的状态图
from langgraph.constants import START
from langgraph.graph import add_messages, StateGraph
from typing_extensions import TypedDict, Annotated

from app.agents.lib.llm.llm import LLMFactory


class State(TypedDict):
    #Messages have type list The add_messages function
    #in the annoation defines how this state key should be updated
    # (in this case,it appends messages to the list,rather than overwrting them)
    messages:Annotated[list,add_messages]

graph_builder = StateGraph(State)

def chatboot(state:State):
    return {"messages":[LLMFactory.getDefaultOPENAI().invoke(state["messages"])]}

graph_builder.add_node("chatboot",chatboot)
graph_builder.add_edge(START,"chatboot")
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
