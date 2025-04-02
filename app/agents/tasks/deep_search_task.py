#深度搜索分析
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.deepSearchTask_prompt import DEEPSEARCHTASK_PROMPT
from app.agents.schemas import AgentState

#获取rawData数据s
def searchResult(attached_data):
    return {}


async def research_task(state: AgentState) -> AgentState:
    print("send_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=DEEPSEARCHTASK_PROMPT,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage
    })
    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
    #获取对应的
    #获取对应的深度搜索的结果响应
    data["deepSearchResult"]=searchResult(state.attached_data)
    return state.copy(update={"result": data})