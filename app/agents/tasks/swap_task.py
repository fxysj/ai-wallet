# 处理兑换任务
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.swap_task_propmt import SWAPTASK_TEMPLATE
from app.agents.schemas import AgentState
from app.agents.toolnode.crossChainTool import cross_chain_tool, cross_chain_swap
from app.agents.types.index import TaskAction
from app.utuls.FieldCheckerUtil import FieldChecker


async def swap_task(state: AgentState) -> AgentState:
    print("swap_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    # 先返回响应
    if state.attached_data:
        stateFieldInfo = FieldChecker.get_field_info(state.attached_data, "state")
        if stateFieldInfo and stateFieldInfo == TaskAction.CONFIRM_SWAP.value:
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

    # route_data = cross_chain_swap(addreess=data["form"].get("from"), to=data["form"].get("to"),
    #                               amount=data["form"].get("amount"))
    #
    # routes = route_data["routes"]
    # print(routes)
    # swap_info = data["form"]
    # print(swap_info)
    result = {
        "state": data["state"],
        "indent":state.detected_intent.value,
        "description": data["description"],
        # "routes": routes,
        "form": data["form"],
        # "bestRoute": routes[0] if route_data else None,
        # "estimatedReturn": str(routes[0]["expectedOutput"]) if routes else "0",
        # "estimatedDuration": routes[0]["estimatedDuration"] if routes else "",
        # "transactionDetails": {
        #     "from": swap_info["from"],
        #     "to": swap_info["to"],
        #     "amount": str(swap_info["amount"]),
        #     "estimatedGas": routes[0]["fee"] if routes and "fee" in routes[0] else "Unknown"
        # }
    }
    print(result)

    # 下面是调用对应的工具完成
    # prompt = PromptTemplate(
    #     template=SwapTools,
    #     input_variables=["amount", "from_token", "to_token"],
    # )
    # chain = prompt | llm | JsonOutputParser()
    #
    # # 调用链处理用户最新输入
    # chain_response = chain.invoke({
    #     "current_data": str(state.attached_data),
    #     "history": state.history,
    #     "input": state.user_input,
    #     "langguage": state.langguage
    # })
    # print(chain_response)
    return state.copy(update={"result": result})
