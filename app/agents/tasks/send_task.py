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
    #这里需要对填充完毕的事件进行监听
    #如果存在
    #大模型的InterRupt 可以通过监听AgentState 中的附加数据进行作为拦截器进行拦截
    #如果拦截到则不再处理
    # res = state.attached_data
    # if res:
    #     stateFieldInfo = FieldChecker.get_field_info(res,"state")
    #     isSignx = FieldChecker.get_field_info(res.get("form"),"signedTx") #是否签名
    #     if isSignx:
    #         #修改res中的state 修改为广播操作 返回即可
    #         res["state"] = TaskState.SEND_TASK_BROADCASTED
    #         return state.copy(update={"result": res})
    #
    #     #如果获取到填充完成需要返回给前端表单数据也不在走大模型流程
    #     if stateFieldInfo and  stateFieldInfo==TaskState.SEND_TASK_READY_TO_SIGN:
    #         print("#不再再次走大模型流程")
    #         return state.copy(update={"result": state.attached_data})

    # 如果当前的session没有用户提交的数据内容需要返回
    #不管有没有数据必须让其通过大模型进行处理和填充即可
    # if state.attached_data is None or state.attached_data == {}:
    #     res = {
    #         "description":"您好，目前转账信息还不完整，您需要补充转账地址、来源地址（必须以 '0x' 开头）、转账金额（需大于0）、数字货币类型（仅支持 BTC、ETH、USDT）以及区块链网络（仅支持 ETH、BSC、TRX）",
    #         "state": "REQUEST_MORE_INFO",
    #         "intent":str(state.detected_intent.value),
    #         "form": {
    #             "chainIndex": "",
    #             "fromAddr": "",
    #             "toAddr": "",
    #             "txAmount": "",
    #             "tokenSymbol": "",
    #             "tokenAddress": "",
    #             "extJson": ""
    #         },
    #         "missFields": [
    #             {
    #                 "name": "缺失字段名",
    #                 "description": "缺失字段描述"
    #             }
    #         ],
    #         "DxTransActionDetail": {}
    #     }
    #     return state.copy(update={"result": res})
    # 这里采用大模型进行返回对应的响应信息
    # 初始化模型组件：提示词、LLM 与输出解析器
    # ------------------------------------------------------------------------------
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["current_data", "history", "input","langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    print("111111111111")
    # 使用新版输出解析器
    #如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()
    print(chain)

    # 组装最近的对话历史（取最新5条记录）
    # history = "\n".join(
    #     [f"{msg['role']}: {msg['content']}" for msg in dict_manager.get(state.session_id).get("history")[-5:]]
    # )

    print(state.history)
    print(state.user_input)
    print("=============用户传递的数据需要进行字符串的格式")
    print(str(state.attached_data))
    # 调用链处理用户最新输入
    chain_response =  chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage":state.langguage
    })
    print(chain_response)
    # 有LLM地方必须更新
    # session = dict_manager.get(state.session_id)
    # session["history"].extend([
    #     {"role": "user", "content": state.user_input},
    #     {"role": "assistant", "content": chain_response.get("description", "")}
    # ])
    # dict_manager.update(state.session_id,session)
    # 更新完毕

    # 合并更新数据（此处返回的 merged_data 包含 errors 字段）
    # merged_data = TransactionSystem.smart_merge(state.attached_data, chain_response)
    #返回的数据 LLM大模型进行生成对应的数据结构 不再需要人为去设置
    #这样可以在Data修改对应的属性进行额外的信息的新增
    #AgentState进行共享当前的历史会话和用户身份信息
    #需要优化点的Session需要使用数据库的方式或者Redis进行保存用户的
    #会话和历史信息
    #并且支持新增的模式

    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    #这里需要进行修正data中的DxTransActionDetail熟悉
    #需要重新组合为新的 对象的Class.to_Dict()
    #data["DxTransActionDetail"] = {}

    # missFields=[]
    # for index,value in data.get("missFields"):
    #     missFieldObject =MissingField(name=value.get("name"),type_="string",description=value.get("description"))
    #     missFields.append(missFieldObject)

    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp",timestamp_time)
    data["transactionResult"] = state.attached_data.get("transactionResult",{})
    #组织返回的对象返回
    # sendTaskData=SendTaskData(intent=state.detected_intent.value,
    #              state=data.get("state"),
    #              form=data.get("form"),
    #              missingFields=missFields,
    #              transactionResult=TransactionResult(status="",txHash="",errorMessage=""),
    #              timestamp=timestamp_time
    #              )

    return state.copy(update={"result": data})
