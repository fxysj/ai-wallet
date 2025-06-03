from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool, Tool
from app.agents.lib.llm.llm import LLMFactory

# 1. 工具定义
@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和"""
    return a + b

def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积"""
    return a * b

multiply_tool = Tool.from_function(
    func=multiply,
    name="MultiplyTool",
    description="用于将两个整数相乘"
)

tools = [add, multiply_tool]



# 3. 创建 ReAct Agent
llm = LLMFactory.getDefaultOPENAI()
agent = create_react_agent(model=llm, tools=tools)

# 4. 包装 AgentExecutor

# 5. 执行调用
response = agent.invoke([HumanMessage(content="你在干嘛")])

# 6. 输出结果
print(response)
