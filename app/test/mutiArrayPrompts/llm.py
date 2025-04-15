#测试多表单提交智能体
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.test.mutiArrayPrompts.send_task_propmt import PROMPT_TEMPLATE_MITI_ARRAY


def TestSendMutilForm():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    print("=========PROMPT_TEMPLATE==================")
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": [],
        "history": [],
        "input": "我想转三笔，一笔给 0xabc，0.5ETH；一笔给 0xdef，1ETH；一笔给 0xghi，0.2ETH。 供链 ID:1,原地址信息：0xaaa,滑点为:0.01 确定",
        "langguage": "cn"
    })
    print(chain_response)
#✅ Case 1：部分信息缺失（SEND_TASK_NEED_MORE_INFO）
def TestSendMutilForm_NeedMoreInfo():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    print("=== SEND_TASK_NEED_MORE_INFO ===")
    chain_response = chain.invoke({
        "current_data": [],
        "history": [],
        "input": "我想转三笔，一笔给 0xabc，0.5ETH；一笔给 0xdef，1ETH；一笔给 0xghi，0.2ETH。",  # 缺链ID、滑点、fromAddress
        "langguage": "en"
    })
    print(chain_response)

#✅ Case 2：信息齐全，进入签名状态（SEND_TASK_READY_TO_SIGN）
def TestSendMutilForm_ReadyToSign():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    print("=== SEND_TASK_READY_TO_SIGN ===")
    chain_response = chain.invoke({
        "current_data": [],
        "history": [],
        "input": "我想转三笔，一笔给 0xabc，0.5ETH；一笔给 0xdef，1ETH；一笔给 0xghi，0.2ETH。供链 ID:1,原地址信息：0xaaa,滑点为:0.01 确定",
        "langguage": "en"
    })
    print(chain_response)

#✅ Case 3：已签名并广播（SEND_TASK_BROADCASTED）
def TestSendMutilForm_Broadcasted():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    print("=== SEND_TASK_BROADCASTED ===")
    chain_response = chain.invoke({
        "current_data": [
            {"chainId": 1, "fromAddress": "0xaaa", "toAddress": "0xabc", "amount": 0.5, "slippage": 0.01}
        ],
        "history": [],
        "input": "我已签名，请广播交易",
        "langguage": "cn"
    })
    print(chain_response)

#✅ Case 4：用户取消（SEND_TASK_CANCELLED）
def TestSendMutilForm_Cancelled():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    print("=== SEND_TASK_CANCELLED ===")
    chain_response = chain.invoke({
        "current_data": [],
        "history": [],
        "input": "算了，我不转了，取消交易",
        "langguage": "cn"
    })
    print(chain_response)

#✅ Case 5：多笔中部分缺失字段（混合场景
def TestSendMutilForm_PartialInfo():
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_MITI_ARRAY,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    chain = prompt | llm | JsonOutputParser()
    print("=== SEND_TASK_NEED_MORE_INFO (Partial Info) ===")
    chain_response = chain.invoke({
        "current_data": [],
        "history": [],
        "input": "我想转账给0xabc 1ETH, 给0xdef 2ETH（链ID是1，滑点为0.01，fromAddress是0xaaa），再给0xghi 0.1ETH（fromAddress是0xaaa，链ID是1）",
        "langguage": "cn"
    })
    print(chain_response)


if __name__ == '__main__':
    #TestSendMutilForm()
    #TestSendMutilForm_NeedMoreInfo()
    TestSendMutilForm_ReadyToSign()
    # TestSendMutilForm_Broadcasted()
    # TestSendMutilForm_Cancelled()
    # TestSendMutilForm_PartialInfo()


