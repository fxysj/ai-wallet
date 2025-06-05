# 处理兑换任务
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.emun.LanguageEnum import LanguageEnum
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.swap_task_propmt_en import SWAPTASK_TEMPLATE
from app.agents.schemas import AgentState, Intention
from app.agents.form.form import *
from app.utuls.FieldCheckerUtil import FieldChecker

SYSTEM_PROMPT = """
  你是一个加密货币交易类型的意图识别助手。用户会输入一段关于加密货币操作的自然语言内容，请你判断用户的操作是“闪兑”（Swap）还是“跨链”（Bridge）。

   判断标准如下：
   - 如果用户要在**同一个链**上将一种token换成另一种代币，比如“将ETH链上的ETH 换成 USDC”，那么是【闪兑 Swap】。
   - 如果用户要将**A链**上的一种token换成**B链**上的一种token，即使币种名称不变，也是【跨链Bridge】。
   - 你只需要回答两个词之一：Swap 或 Bridge。不要输出其他内容。

   现在请根据用户输入判断：
   {query}
   你的判断：
   """


# 根据用户的输入内容具体判断是否是 闪退、桥接
def getIsSwapOrBridege(query: str):
    pro = PromptTemplate(
        template=SYSTEM_PROMPT,
        input_variables=["query"],
    )
    c = pro | LLMFactory.getDefaultOPENAI() | StrOutputParser()
    return c.invoke({"query": query})


def build_prompt(user_query: str) -> str:
    return SYSTEM_PROMPT.strip() + "\n用户输入：" + user_query + "\n你的判断："


async def swap_task(state: AgentState) -> AgentState:
    print("swap_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    print("信息========")
    formData = state.attached_data
    swapIdData = state.attached_data.get("swapId")
    language = state.langguage
    if swapIdData:
        # 处理存档的逻辑
        txtId = swapIdData.get("txId")
        if txtId:
            print("业务进行存档处理")
            if language == LanguageEnum.EN.value:
                formData["description"] = "Alright, I will continue to monitor the transaction status for you."
            if language == LanguageEnum.ZH_HANS.value:
                formData["description"] = "好的，我会继续为您监控交易状态。"

            if language == LanguageEnum.ZH_HANT.value:
                formData["description"] = "好的，我會繼續為你監控交易狀態。"

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
    data = response_data.get("data")
    data["intent"] = Intention.swap.value

    if not formData.get("form"):
        # 这里进行识别出类型Swap Bridge
        isSwpRes = getIsSwapOrBridege(state.user_input)
        print("类型:",isSwpRes)
        # 如果类型为Swap
        if isSwpRes == "Swap":
            data["form"]["fromChain"] = "60"
            data["form"]["fromTokenAddress"] = "native"
            data["form"]["toTokenAddress"] = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
            data["form"]["toChain"] = "60"

        if isSwpRes == "Bridge":
            data["form"]["fromChain"] = "60"
            data["form"]["fromTokenAddress"] = "native"
            data["form"]["toTokenAddress"] = "0x55d398326f99059ff775485246999027b3197955"
            data["form"]["toChain"] = "56"

        if state.langguage == LanguageEnum.EN.value:
            data["description"] = "Hello, I’ve prepared the transaction page you need. Please fill in the necessary Exchange details, and I will assist you with the remaining steps. Once you're ready, feel free to proceed."

        if state.langguage == LanguageEnum.ZH_HANS.value:
            data["description"] = "您好，我已为您准备好交易页面。请填写必要的兑换交易信息，其余步骤我将协助完成。准备好后随时开始吧"

        if state.langguage == LanguageEnum.ZH_HANT.value:
            data["description"] = "您好，我已為您準備好交易頁面。請填寫必要的兌換交易資訊，其餘步驟我將協助完成。準備好後隨時開始吧。"

        return state.copy(update={"result": data})



    # 这里进行处理 formData
    # 如果确实字段存在
    if data["missFields"]:
        if state.langguage == LanguageEnum.EN.value:
            data["description"] = "OK！Your Exchange request has been received. I’ve prepared the transaction page and pre-filled the main details for you. Please review the information and complete the remaining fields to proceed with the transaction."

        if state.langguage == LanguageEnum.ZH_HANS.value:
            data["description"] = "好的！您的兑换请求已收到。我已经准备好交易页面，并预先填写了主要信息。请仔细阅读信息并填写剩余信息以继续进行交易"

        if state.langguage == LanguageEnum.ZH_HANT.value:
            data["description"] = "好的！您的兌換請求已收到。我已經準備好交易頁面，並預先填寫了主要資訊。請仔細閱讀資訊並填寫剩餘資訊以繼續進行交易。"

    return state.copy(update={"result": data})


if __name__ == '__main__':
    print(getIsSwapOrBridege("我要在Avalanche链做Swap"))
    print(getIsSwapOrBridege("我要在Avalanche链做Swap"))
