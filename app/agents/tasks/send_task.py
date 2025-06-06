import time
import json
from typing import Optional, Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.emun.LanguageEnum import LanguageEnum
from app.agents.schemas import AgentState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.form.form import *
from app.agents.proptemts.send_task_propmt_en import PROMPT_TEMPLATE
from app.agents.services.send_task_service import is_valid_empty_form, is_valid_empty_form_ok
from app.agents.tools import *
from app.utuls.FieldCheckerUtil import FieldChecker


# 任务处理函数
async def send_task(state: AgentState) -> AgentState:
    print("send_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    language = state.langguage
    #先进行判断 如果返回了txHash则不再走大模型处理
    # formData = state.attached_data
    if state.attached_data:
        formData  = state.attached_data
        if formData.get("transactionResult"):
            transactionResult = formData.get("transactionResult")
            if transactionResult:
                if language == LanguageEnum.EN.value:
                    formData["description"] = "Alright, I will continue to monitor the transaction status for you."
                if language == LanguageEnum.ZH_HANS.value:
                    formData["description"] = "好的，我会继续为您监控交易状态。"
                if language == LanguageEnum.ZH_HANT.value:
                    formData["description"] = "好的，我會繼續為你監控交易狀態。"

                formData["state"] = TaskState.SEND_TASK_BROADCASTED
                formData["intent"] = Intention.send.value
                return state.copy(update={"result": formData})

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"],
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
        "langguage": state.langguage,
        "chain_data": state.chain_data
    })

    print(chain_response)
    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = Intention.send.value
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


    if is_valid_empty_form_ok(data.get("form")):
        if state.langguage == LanguageEnum.EN.value:
            data["description"] = "Hello, I’ve prepared the transaction page you need. Please fill in the necessary transfer details, and I will assist you with the remaining steps. Once you're ready, feel free to proceed."

        if state.langguage == LanguageEnum.ZH_HANS.value:
            data["description"] = "您好，我已为您准备好转账页面。请填写必要的转账信息，其余步骤我将协助完成。准备好后随时开始吧"

        if state.langguage == LanguageEnum.ZH_HANT.value:
            data["description"] = "您好，我已為您準備好轉帳頁面。請填寫必要的轉帳資訊，其餘步驟我將協助完成。準備好後隨時開始吧。"
    else:
        if state.langguage==LanguageEnum.EN.value:
            data["description"] = "OK！Your transfer request has been received. I’ve prepared the transfer page and pre-filled the main details for you. Please review the information and complete the remaining fields to proceed with the transaction "

        if state.langguage==LanguageEnum.ZH_HANS.value:
            data["description"] = "好的！您的转账请求已收到。我已经准备好转账页面，并预先填写了主要信息。请仔细阅读信息并填写剩余信息以继续进行交易"


        if state.langguage==LanguageEnum.ZH_HANT.value:
            data["description"] = "好的！您的轉帳請求已收到。我已經準備好轉帳頁面，並預先填寫了主要資訊。請仔細閱讀資訊並填寫剩餘資訊以繼續進行交易。"



    return state.copy(update={"result": data})
