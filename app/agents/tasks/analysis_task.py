# 处理分析意图任务
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.proptemts.v1.intent_prompt_deep_up import INTENT_PROMPT_TEMPLATE
from app.agents.schemas import AgentState, Intention
from app.agents.lib.llm.llm import LLMFactory
from app.config import settings
from app.utuls.FieldCheckerUtil import FieldChecker
from app.agents.const.constField import intentFieldName
async def parse_complex_intent(state: AgentState) -> AgentState:
    try:
        #1.0 如果在表单中已经传递 intent_state 则不再走当前的路由直接返回即可
        isExist =  FieldChecker.get_field_info(
            data=state.attached_data,
            field_name=intentFieldName
        )
        print(isExist)
        #如果传递对应的状态则不再进行大模型分析
        if isExist:
            return state.copy(update={"detected_intent": Intention(isExist)})
        print("=========进行意图分析===============")
        history_str =  state.history
        print(history_str)
        attached_data_json = str(state.attached_data)
        print(attached_data_json)
        prompt = PromptTemplate.from_template(INTENT_PROMPT_TEMPLATE)
        # 构造 LLMChain，将 llm 和 prompt 结合起来
        # 直接使用 `prompt | llm | StrOutputParser`
        llm = LLMFactory.getOpenAI(open_key=settings.OPENAI_API_KEY,url=settings.OPENAI_API_BASE_URL)
        chain = prompt | llm | StrOutputParser()

        # 异步调用，传入参数
        response = await chain.ainvoke({
            "message_history": history_str,
            "latest_message": state.user_input,
            "attached_data": attached_data_json
        })
        intent_str = response.strip().lower()

        # state = update_history(state,intent_str)

        if intent_str in Intention.__members__.values():
            intent = Intention(intent_str)
        else:
            intent = Intention.unclear
        print("更新当前的历史信息")
        print(intent_str)
        result = state.copy(update={"detected_intent": intent})
        print("==============")
        print(result)
        return result
    except Exception as e:
        return state.copy(update={"detected_intent": Intention.unclear})