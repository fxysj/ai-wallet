#进行测试工具
#使用最新的构建方式:Runnable+Tool+AgentExecutor
#1.0 定义工具：使用tool装饰器
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, \
    HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.tools import tool
from langchain_core.tools import Tool

from app.agents.lib.llm.llm import LLMFactory


@tool
def add(a:int, b:int)->int:
    """计算俩个整数的和"""
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

multiply_tool = Tool.from_function(
    func=multiply,
    name="MultiplyTool",
    description="用于将两个整数相乘"
)
#第二步创建 ReactAgent+AgentExecutor
#将工具列表组合起来
tools=[add,multiply_tool]

# 自定义 Prompt（必需！）
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是一个可以调用工具的智能 AI 助手。"),
    HumanMessagePromptTemplate.from_template("{input}"),
    AIMessagePromptTemplate.from_template("{agent_scratchpad}")
])
#创建React Agent
agent = create_openai_functions_agent(llm=LLMFactory.getDefaultOPENAI(),tools=tools,prompt=prompt)
#创建AgentExecutor
agent_sin = AgentExecutor(agent=agent,tools=tools,verbose=True)

response = agent_sin.invoke({"input": "请计算 3 加 5，然后再乘以 2"})
print(response)
