import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.schemas import AgentState
import json
from typing import Optional, Dict, Any

from app.agents.lib.llm.llm import LLMFactory
from app.agents.form.form import *
from app.agents.proptemts.send_task_propmt import PROMPT_TEMPLATE
from app.agents.tools import *

from app.utuls.FieldCheckerUtil import FieldChecker


# 任务处理函数
async def send_task(state: AgentState) -> AgentState:
    print("send_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    #先进行判断 如果返回了txHash则不再走大模型处理
    # formData = state.attached_data
    if state.attached_data:
        formData  = state.attached_data
        if formData.get("transactionResult"):
            transactionResult = formData.get("transactionResult")
            if transactionResult.get("txHash"):
                formData["description"] = "success"
                formData["state"] = TaskState.SEND_TASK_BROADCASTED
                formData["intent"] = Intention.send.value
                return state.copy(update={"result": formData})

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["current_data", "history", "input","langguage"],
    )
    print("=========PROMPT_TEMPLATE==================")
    print(PROMPT_TEMPLATE)
    llm = LLMFactory.getDefaultOPENAI()
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response =  chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage":state.langguage
    })
    print(chain_response)
    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp",timestamp_time)
    data["transactionResult"] = state.attached_data.get("transactionResult",{})
    #如果存在结果
    if data["transactionResult"]:
        transactionResult = data["transactionResult"]
        #如果不存在则需要进行更新
        if not transactionResult.get("txHash"):
            data["state"] = TaskState.SEND_TASK_READY_TO_BROADCAST


    return state.copy(update={"result": data})
