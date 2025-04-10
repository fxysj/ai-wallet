#多轮识别
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.intent_prompt_chat_mutil import INTENT_PROMPT_TEMPLATE_MUTil
from app.agents.response.DataResponse import CommonData
from app.agents.schemas import AgentState


async def mutil_intent_asnyc_task(state: AgentState) -> AgentState:
    print("mutil_intent_asnyc_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=INTENT_PROMPT_TEMPLATE_MUTil,
        input_variables=["current_data", "history", "input"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    # 使用新版输出解析器
    # 如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = await chain.ainvoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
    })
    sys_message = chain_response.get("system_message")
    message = []
    message.append(sys_message)
    multi_round_guidance = chain_response.get("multi_round_guidance")
    if multi_round_guidance:
      for index,value in multi_round_guidance:
          print(index,value)
          message.append(value)

          # 返回的结果如下：
    data = CommonData(
          description=str(message),
          state="",
          intent=chain_response.get("intent"),
          form={},
          missFields=[],
          timestamp="1744258518.8706527"
      )
    attach_data = state.attached_data
    attach_data["intent"] = chain_response.get("intent")
    return state.copy(update={"attached_data": attach_data,"result":data.dict()})
