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
    #如果需要分析才调用大模型
    if state.isAsync:
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
        updateUserLanguage(state.session_id,userLanggurage.language)
        return state.copy(update={"langguage":userLanggurage.language})
    return state.copy()

def  updateUserLanguage(session_id:str,langguage:str)->bool:
    redis_dict_manager.add(session_id,langguage)
    return True











