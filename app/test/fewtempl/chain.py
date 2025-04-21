from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI

from app.agents.lib.llm.llm import LLMFactory
from app.test.fewtempl.fewtem import few_shot_prompt
from langchain.tools import tool

llm = LLMFactory.getDefaultOPENAI()

@tool
def get_weaher(lo):
    """根据经纬度获取地理位置信息"""
    return "ok"

tools = [get_weaher]


agent=initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prompt": few_shot_prompt},  # ✅ 只传一次
    verbose=True
)

# 调用
response = agent.run("我想控制血压，帮我定个饮食计划")
print(response)
