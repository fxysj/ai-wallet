#提示词fallback兜底提示词测试
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from app.agents.schemas import AgentState
from app.agents.tasks.fallback_task import fallback_task
from app.agents.tasks.fallback_task import *
def callState():
    return AgentState(
        user_input="xdadasd",
        messages=[],
        attached_data={},
        history="",
    )
def Fallback():
   return fallback_task(callState())


def getname(query):
    """查询用户信息"""
    return "xin"

if __name__ == '__main__':
    #print(Fallback().result)
    #print(searchTools())
    toosgaet=[getname]
    # agent = create_react_agent(tools=toosgaet,model=LLMFactory.getDefaultOPENAI())
    # res = agent.invoke({"messages":["我的名字是:sin,查询我的信息"]})
    agent = LLMFactory.create_custom_agent(llm=LLMFactory.getDefaultOPENAI(),prompt=ChatPromptTemplate.from_messages(
        [
            ("system","你是一个敏感词生成大师 需要根据用户输入的敏感词进行定义 并且返回类似的敏感词 数组,返回"),
            MessagesPlaceholder(variable_name="messages"),
            ("user","ok")
        ]
    ),debug=True,tools=toosgaet)
    res = agent.invoke({"messages":["特朗普"]})
    print(res["messages"][-1].content)


