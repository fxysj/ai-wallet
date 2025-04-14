import unittest
from app.agents.lib.llm.llm import LLMFactory
from app.test.deepSearchProject.deepSearchTask_prompt_test import DEEPSEARCHTASK_PROMPT_TEST
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
def generate_chain():
    llm = LLMFactory.getDefaultDeepSearchOPENAI()
    prompt = PromptTemplate(
        template=DEEPSEARCHTASK_PROMPT_TEST,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"],
    )
    return prompt | llm | JsonOutputParser()

def run_deep_search_test(input_text, current_data=None, history=None, langguage="cn"):
    print("========= DEEP SEARCH TEST INPUT =========")
    print(f"Input: {input_text}")
    print("==========================================")
    if current_data is None:
        current_data = {}
    if history is None:
        history = []

    chain = generate_chain()
    result = chain.invoke({
        "current_data": current_data,
        "history": history,
        "input": input_text,
        "langguage": langguage
    })

    print("=============== RESULT ===================")
    print(result)
    print("==========================================")
    return result


def test_case_1_basic_search():
    run_deep_search_test("0x980DD1c27614121231F5A64Db9DD7c679C3551d2")


def test_case_2_modify_input():
    run_deep_search_test("我要查的是 Solana")


def test_case_3_missing_fields():
    run_deep_search_test("帮我查一下 Root")


def test_case_4_wrong_type_fix():
    run_deep_search_test("上次你查的是 Uniswap 协议，但我要找的是 Uniswap 的地址")


def test_case_5_english_environment():
    run_deep_search_test("SushiSwap", langguage="en")


def test_case_6_fully_filled_ready_search():
    run_deep_search_test("我找的是 Aave 协议，不是 Token，快点开始吧！")

if __name__ == '__main__':
    #test_case_1_basic_search()
    test_case_2_modify_input()
    # test_case_3_missing_fields()
    # test_case_4_wrong_type_fix()
    # test_case_5_english_environment()
    # test_case_6_fully_filled_ready_search()