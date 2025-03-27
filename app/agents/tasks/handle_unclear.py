# 深度搜索分析
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.session.sessionManager import dict_manager
from app.agents.schemas import AgentState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.tools import GetWrapResponse
from app.config import settings
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from app.agents.proptemts.unclear_propmt import  UnClearTemplate

async def unclear_task(state: AgentState) -> AgentState:
    system_message = UnClearTemplate
    llm = LLMFactory.getOpenAI(open_key=settings.OPENAI_API_KEY, url=settings.OPENAI_API_BASE_URL)
    prompt = PromptTemplate(
        template=system_message,
        input_variables=["input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    # 将 state.user_input 封装成字典
    input_data = {"input": state.user_input, "language": state.language}
    result = await chain.ainvoke(input_data)
    print("进入无法匹配模式")
    return state.copy(update={"result": result})
