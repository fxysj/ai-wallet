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
if __name__ == '__main__':
    TestSendMutilForm()


