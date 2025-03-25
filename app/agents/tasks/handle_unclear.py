# 深度搜索分析
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.session.sessionManager import dict_manager
from app.agents.schemas import AgentState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.tools import GetWrapResponse
from app.config import settings


async def unclear_task(state: AgentState) -> AgentState:
    system_message = """
    You are Tikee AI, a helpful crypto wallet assistant.

    The user's request doesn't match any specific crypto transaction or research task.

    Provide general assistance about cryptocurrency topics, wallet functionality, or redirect them to specific features if appropriate.

    Always respond in a friendly, helpful tone.
    """
    print("222")
    llm = LLMFactory.getOpenAI(open_key=settings.OPENAI_API_KEY, url=settings.OPENAI_API_BASE_URL)
    prompt = PromptTemplate.from_template(system_message)
    chain = prompt | llm | StrOutputParser()
    # 将 state.user_input 封装成字典
    input_data = {"input": state.user_input} if state.user_input else {}
    result = await chain.ainvoke(input_data)
    print("进入无法匹配模式")
    response = GetWrapResponse(
        data=result,
        history=dict_manager.get(state.session_id).get("history"),  # 历史信息
        system_response="",
        missfield="",
        description="",
        is_completed=False,
        detected_intent=state.detected_intent.value
    )
    return state.copy(update={"result": response})
