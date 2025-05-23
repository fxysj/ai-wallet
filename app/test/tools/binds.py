import json
from typing import TypedDict, Annotated, Dict, Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from app.agents.tools import display_and_save_graph
#案例进演示了多个工具进行插入到不同的大模型
# query->RAG+MEMORY+ProtemPlate+context+chatHistory
# LLM->tools->functions-call
# toolsNode
# toolsRoute
# toolsNode

@tool
def getWeatherInfo(city: str) -> Dict[str, Any]:
    """根据城市名称获取当前城市的天气情况"""
    print(f"Fetching weather for city: {city}")
    # 这里你可以调用真实天气API，比如高德天气API、OpenWeatherMap等
    # 为了示例，这里模拟返回
    mock_weather_data = {
        "Shanghai": {"temperature": "22°C", "condition": "Cloudy"},
        "Beijing": {"temperature": "19°C", "condition": "Sunny"},
        "Guangzhou": {"temperature": "28°C", "condition": "Thunderstorm"},
    }
    weather = mock_weather_data.get(city, {"temperature": "Unknown", "condition": "Unknown"})
    return {
        "city": city,
        "temperature": weather["temperature"],
        "condition": weather["condition"]
    }


def init_chat_modle_consutom(model: str, tootls=None):
    return init_chat_model(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE_URL
    ).bind_tools(tootls)


from app.config import settings


class State(TypedDict):
    # Messages have the type list The add_messages function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwrtting them)
    messages: Annotated[list, add_messages]


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        print("BasicToolNode 收到 inputs:", inputs)
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


def chatbot(state: State):
    print("当前 State:", state)
    llm = init_chat_modle_consutom("gpt-4o", tools)
    return {"messages": [llm.invoke(state["messages"])]}


def stream_graph_updates(user_input: str):
    config = {"configurable": {"thread_id": "0x1w2121212"}}
    print(graph.get_prompts(config=config))
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()


from langchain_tavily import TavilySearch

tra = TavilySearch(max_results=2)
tools = [getWeatherInfo]
tool_node = BasicToolNode(tools=tools)

memory = MemorySaver()


def route_tools(
        state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END



#在定义一个大模型信息大模型绑定搜索的工具
def mainHanlerSend(state:State):
    print("State=====:",state)
    tool= TavilySearch(max_results=2)
    tools=[tool]
    #实例化大模型
    #绑定搜索到这个大模型上面
    llm = init_chat_modle_consutom("gpt-4o",tools)
    #定义提示词信息
    p=PromptTemplate(
        template="""你是一个区块链交易大师
        你能够精确识别出用户的意图,并且准确捕获用户的有用信息
        当你不知道的时候 根据下面的上下文进行回答
        {history}
        messages:{messages}
        收集用户的信息 并且引导用户 下一步应该做什么
        根据messages history 信息 揣测用户的性格 
        返回
        ```json
        {{"data":
              {{
              "form":{{更新收集到的用户信息}}
              }}
        }}
        ```
        """,
        input_variables=["history","messages"],
    )
    chain = p | llm | JsonOutputParser()
    print(graph.get_state_history(config={"configurable": {"thread_id": "0x1w2121212"}}))
    res = chain.invoke({"history":graph.get_state_history(config={"configurable": {"thread_id": "0x1w2121212"}}),"messages":state["messages"]})
    return  {"messages":json.dumps(res)}


if __name__ == '__main__':
    graph_builder = StateGraph(State)
    # the first argument is the unique node name
    # the second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("send",mainHanlerSend)
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
        # It defaults to the identity function, but if you
        # want to use a node named something else apart from "tools",
        # You can update the value of the dictionary to something else
        # e.g., "tools": "my_tools"
        {"tools": "tools", END: "send"},
    )
    graph_builder.add_edge("send",END)
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph = graph_builder.compile(checkpointer=memory)
    try:
        # 保存对应的流图片
        display_and_save_graph(app=graph, filename="graph.png", output_dir="graphs")
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

    except Exception as e:
        print(e)
        pass
