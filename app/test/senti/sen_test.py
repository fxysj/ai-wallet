#提示词fallback兜底提示词测试
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from app.agents.schemas import AgentState
from app.agents.tasks.fallback_task import fallback_task
from app.agents.tasks.fallback_task import *
def callState():
    return AgentState(
        user_input="sb",
        messages=[],
        attached_data={},
        history="",
        langguage="en",
    )
def Fallback():
   return fallback_task(callState())


def getname(query):
    """查询用户信息"""
    return "xin"

if __name__ == '__main__':
    print(Fallback().result)
    #print(searchTools())



