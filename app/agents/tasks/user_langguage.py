from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from app.agents.proptemts.userLangguageAnaysic_en import UserLangguageAnasicTemplate
from app.agents.schemas import AgentState
#用来分析用户的当前的langGuage语言类型 要在返回的时候进行跟进是否大模型进行语言的翻译
from app.agents.lib.llm.llm import LLMFactory
from langchain.prompts import PromptTemplate
from app.agents.lib.redisManger.redisManager import redis_dict_manager
class UserAnalysisResult(BaseModel):
    language: str
    language_score: int
    personAsync: str
    personAsync_score: int
    total_score: int

async def  userLangGuageAnaysic(state: AgentState)->AgentState:
    #直接从缓存中获取即可
    language = getUserLanguage(state.session_id)
    if language:
        return state.copy(update={"langguage": language})

    if state.isAsync:
        #需要从Redis获取信息
        llm = LLMFactory.getDefaultOPENAI()
        prompt = PromptTemplate(
            template=UserLangguageAnasicTemplate,
            input_variables=["history", "user_input"],
        )
        chain = prompt | llm | JsonOutputParser(pydantic_model=UserAnalysisResult)
        response = chain.invoke({
            "history":state.history,
            "user_input":state.user_input
        })
        #显示返回
        userLanggurage = UserAnalysisResult(**response)
        print("语言分析的结果：")
        print(userLanggurage)
        updateUserLanguage(state.session_id,userLanggurage.language)
        return state.copy(update={"langguage":userLanggurage.language})
    return state.copy()

def  updateUserLanguage(session_id:str,langguage:str)->bool:
    redis_dict_manager.add(session_id,langguage)
    return True
def getUserLanguage(session_id:str)->str:
    return redis_dict_manager.get(session_id)











