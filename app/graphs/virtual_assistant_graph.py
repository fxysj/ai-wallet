#智能小助手
from typing import List
from langchain_core.messages import SystemMessage
from pydantic import BaseModel

from app.agents.lib.llm.llm import LLMFactory

template = """Your job is to get information from a user about what type of prompt template they want to create.
You should get the following information from them:
What the objective of the prompt is
What variables will be passed into the prompt template
Any constraints for what the output should NOT do
Any requirements that the output MUST adhere to
If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.
After you are able to discern all the information, call the relevant tool."""
"""
你的工作是从用户那里获取他们想要创建哪种类型的提示模板的信息。
您应该从他们那里获得以下信息：
- 提示的目的是什么
- 将向提示模板传递哪些变量
- 输出不应该做什么的任何限制
- 输出必须遵守的任何要求
如果你无法辨别这些信息，请他们澄清！不要试图疯狂猜测。
在您能够辨别所有信息后，调用相关工具。
"""
#定义一个函数，用于将系统消息和用户消息组合成一个消息列表
def get_messages_info(messages):
 return [SystemMessage(content=template)] + messages

#定义一个数据模型，用于存储提示模板的指令信息
class PromptInstructions(BaseModel):
    """Instructions on how to prompt the LLM."""
    objective: str
    variables: List[str]
    constraints: List[str]
    requirements: List[str]

#初始化一个 ChatOpenAI 实例，温度设为 0
llm = LLMFactory.getDefaultOPENAIZERO()
#将工具绑定到 LLM 实例上
llm_with_tool = llm.bind_tools([PromptInstructions])

# 将消息处理链定义为 get_messages_info 函数和绑定工具的 LLM 实例
chain = get_messages_info | llm_with_tool

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# 定义一个新的系统提示模板
prompt_system = """Based on the following requirements, write a good prompt template:

{reqs}"""

# 定义一个函数，用于获取生成提示模板所需的消息
# 只获取工具调用之后的消息
def get_prompt_messages(messages: list):
    tool_call = None
    other_msgs = []
    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls:
            tool_call = m.tool_calls[0]["args"]
        elif isinstance(m, ToolMessage):
            continue
        elif tool_call is not None:
            other_msgs.append(m)
    return [SystemMessage(content=prompt_system.format(reqs=tool_call))] + other_msgs

# 将消息处理链定义为 get_prompt_messages 函数和 LLM 实例
prompt_gen_chain = get_prompt_messages | llm

from typing import Literal
from langgraph.graph import END


# 定义一个函数，用于获取当前状态
def get_state(messages) -> Literal["add_tool_message", "info", "__end__"]:
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_tool_message"
    elif not isinstance(messages[-1], HumanMessage):
        return END
    return "info"


# 定义一个函数，用于添加工具消息
def add_tool_message(state: list):
    return ToolMessage(
        content="Prompt generated!", tool_call_id=state[-1].tool_calls[0]["id"]
    )

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessageGraph

# 初始化 MemorySaver 实例
memory = MemorySaver()

# 初始化 MessageGraph 实例
workflow = MessageGraph()

# 添加节点 "info" 和对应的处理链
workflow.add_node("info", chain)

# 添加节点 "prompt" 和对应的处理链
workflow.add_node("prompt", prompt_gen_chain)

#添加工具节点
workflow.add_node("add_tool_message", add_tool_message)

# 添加条件边，从 "info" 节点到其他节点

workflow.add_conditional_edges("info", get_state)

# 添加边，从 "add_tool_message" 节点到 "prompt" 节点
workflow.add_edge( "add_tool_message",   "prompt")

# 添加边，从 "prompt" 节点到 END
workflow.add_edge( "prompt", END)

# 添加边，从 START 到 "info" 节点
workflow.add_edge(START, "info")






