from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.schemas import *
import json
from typing import Optional, Dict, Any

from app.agents.lib.llm.llm import LLMFactory
from app.agents.types.index import TaskAction
from app.config import settings
from app.agents.proptemts.send_task_propmt import PROMPT_TEMPLATE
from app.agents.lib.session.sessionManager import dict_manager
from app.agents.tools import *


# 真实转账功能
from app.utuls.FieldCheckerUtil import FieldChecker


async def real_transfer_assets(data: WalletTransactionSchema) -> dict:
    return {
        "tx_hash": "0x1234567890abcdef",
        "message": "转账成功",
        "is_signed": True
    }


# 处理 attached_data，确保 extJson 是字符串，而不是空字典
def get_wallet_transaction_schema(attedcd_data: Optional[dict] = None) -> Dict[str, Any]:
    if not attedcd_data:
        return {
            "chainIndex": "",
            "fromAddr": "",
            "toAddr": "",
            "txAmount": "",
            "tokenSymbol": "",
            "tokenAddress": "",
            "extJson": ""
        }

    # 确保 extJson 为字符串
    if "extJson" in attedcd_data and isinstance(attedcd_data["extJson"], dict):
        attedcd_data["extJson"] = json.dumps(attedcd_data["extJson"])

    return WalletTransactionSchema(**attedcd_data).model_dump()


# 任务处理函数
async def send_task(state: AgentState) -> AgentState:
    print("send_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    #这里需要对填充完毕的事件进行监听
    #如果存在
    #大模型的InterRupt 可以通过监听AgentState 中的附加数据进行作为拦截器进行拦截
    #如果拦截到则不再处理
    if state.attached_data:
        stateFieldInfo = FieldChecker.get_field_info(state.attached_data,"state")
        if stateFieldInfo and  stateFieldInfo==TaskAction.READY_TO_SIGN_TRANSACTION.value:
            print("#不再再次走大模型流程")
            return state.copy(update={"result": state.attached_data})

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
    return state.copy(update={"result": data})
