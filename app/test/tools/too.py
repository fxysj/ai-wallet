from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool
from pydantic import BaseModel, Field

from app.agents.lib.llm.llm import LLMFactory

# 定义用户信息模型
class UserInfo(BaseModel):
    name: str = Field(default="", description="用户的名称")
    id: int = Field(default=1, description="用户的id")

# 创建工具函数：获取用户信息
@tool
def getUserInfo(user_id: str) -> UserInfo:
    """根据需要获取用户的信息"""
    user_info = UserInfo(name="user_id:" + user_id, id=int(user_id))
    print(f"getUserInfo executed with user_id={user_id}, returning {user_info}")
    return user_info

# 初始化 OpenAI 模型
def init_chat_model(model: str, api_key: str, base_url: str):
    """初始化聊天模型"""
    llm = LLMFactory.getDefaultOPENAI()
    return llm

# 定义提示模板
prompt_template = """
你是一个讲笑话大师：
{user_input}
根据用户输入的内容进行讲出笑话
历史对话:{history}

如果涉及: 获取用户基本信息 调用getUserInfo 工具
笑话:
"""

# 初始化模型和工具
llm = init_chat_model(model="gpt-4o", api_key="your_openai_api_key", base_url="your_openai_base_url")
tools = [getUserInfo]

# 绑定工具到模型
llm_bind_tools = llm.bind_tools(tools)

# 创建用户输入的消息
user_message = HumanMessage(content="查询我的信息ID：1111")

# 通过模型调用工具，并处理结果
# 让模型处理并返回工具的结果
response = llm_bind_tools.invoke([user_message])

# 打印返回的结果
print("Response:", response)

# 确保response是AIMessage对象
if isinstance(response, AIMessage):
    print("Response Content:", response.content)
    print("Response Type:", type(response))
    print("Response Data:", response)
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print("Tool Calls:", response.tool_calls)
        tool_result = response.tool_calls[0]['result']  # 获取工具返回的结果
        print("Tool Result:", tool_result)
    else:
        print("No tool calls found in response.")
else:
    print("Response is not of type AIMessage. It is:", type(response))
