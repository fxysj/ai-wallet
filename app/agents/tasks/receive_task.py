# 处理收款任务
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.receiveTasks_en import RECEIVETASKS_TEMPLATE
from app.agents.schemas import AgentState
from app.agents.tools import GetWrapResponse
from app.agents.toolnode.crossChainTool  import cross_chain_swap
from app.agents.form.form import *
from app.utuls.FieldCheckerUtil import FieldChecker


async def receive_task(state: AgentState) -> AgentState:
    print("receive_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    # 先返回响应
    if state.attached_data:
        stateFieldInfo = FieldChecker.get_field_info(state.attached_data, "state")
        if stateFieldInfo and stateFieldInfo == TaskState.RECEIVE_TASK_SHOULD_DISPLAY_QR_CODE:
            print("#不再再次走大模型流程")
            return state.copy(update={"result": state.attached_data})

    prompt = PromptTemplate(
        template=RECEIVETASKS_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage","chain_data"],
    )
    llm = LLMFactory.getDefaultOPENAI().bind_tools([cross_chain_swap])
    # 使用新版输出解析器
    # 如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()

    print(chain)

    print(state.history)
    print(state.user_input)
    print(str(state.attached_data))
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage,
        "chain_data":state.chain_data
    })
    print(chain_response)

    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    return state.copy(update={"result": data})
