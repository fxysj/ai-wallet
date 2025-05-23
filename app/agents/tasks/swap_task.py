# 处理兑换任务
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.swap_task_propmt_en import SWAPTASK_TEMPLATE
from app.agents.schemas import AgentState, Intention
from app.agents.form.form import *
from app.utuls.FieldCheckerUtil import FieldChecker


async def swap_task(state: AgentState) -> AgentState:
    print("swap_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    print("信息========")
    formData= state.attached_data
    swapIdData = state.attached_data.get("swapId")
    if swapIdData:
        # 处理存档的逻辑
        txtId = swapIdData.get("txId")
        if txtId:
            print("业务进行存档处理")
            formData["description"] = "success"
            formData["state"] = TaskState.SWAP_TASK_BROADCASTED
            formData["intent"] = Intention.swap.value
            return state.copy(update={"result": formData})
    prompt = PromptTemplate(
        template=SWAPTASK_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    # 使用新版输出解析器
    # 如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()
    
    # Prepare prompt variables and add chain_data
    prompt_variables = {
        "current_data": str(formData),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage,
        "chain_data": state.chain_data
    }
    
    # 调用链处理用户最新输入
    chain_response = chain.invoke(prompt_variables)
    response_data = chain_response
    print(response_data)
    data = response_data.get("data")
    data["intent"] = Intention.swap.value
    print("data====")
    print(data)
    return state.copy(update={"result": data})
