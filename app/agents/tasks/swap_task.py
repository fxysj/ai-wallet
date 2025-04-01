# 处理兑换任务
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.swap_task_propmt import SWAPTASK_TEMPLATE
from app.agents.schemas import AgentState
from app.agents.form.form import *
from app.utuls.FieldCheckerUtil import FieldChecker


async def swap_task(state: AgentState) -> AgentState:
    print("swap_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    res = state.attached_data
    # 先返回响应
    if state.attached_data:
        stateFieldInfo = FieldChecker.get_field_info(state.attached_data, "state")
        isSignx = FieldChecker.get_field_info(res.get("form"), "signedTx")  # 是否签名
        if isSignx:
            # 修改res中的state 修改为广播操作 返回即可
            res["state"] = TaskState.SEND_TASK_BROADCASTED
            return state.copy(update={"result": res})

        if stateFieldInfo and stateFieldInfo == TaskState.SEND_TASK_READY_TO_SIGN:
            print("#不再再次走大模型流程")
            return state.copy(update={"result": state.attached_data})

    prompt = PromptTemplate(
        template=SWAPTASK_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
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
        "langguage": state.langguage
    })
    print(chain_response)

    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    data["quoteResult"] = {}
    data["swapResult"] = {}
    data["swapStatus"] = {}
    return state.copy(update={"result": data})
