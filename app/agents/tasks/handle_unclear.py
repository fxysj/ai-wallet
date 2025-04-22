# 深度搜索分析
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.session.sessionManager import dict_manager
from app.agents.schemas import AgentState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.tools import GetWrapResponse
from app.config import settings
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from app.agents.proptemts.unclear_prompt_cle import  UnClearTemplate

async def unclear_task(state: AgentState) -> AgentState:
    system_message = UnClearTemplate
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=system_message,
        input_variables=["message_history", "langguage","latest_message","attached_data"],
    )
    chain = prompt | llm | JsonOutputParser()
    # 将 state.user_input 封装成字典
    input_data = {"message_history": state.history, "langguage": state.langguage,"latest_message": state.user_input, "attached_data": state.attached_data}
    result = await chain.ainvoke(input_data)
    print("进入无法匹配模式")
    print(result)
    return state.copy(update={"result": result})
