import unittest
import time
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
    if current_data is None:
        current_data = {}
    if history is None:
        history = []

    chain = generate_chain()
    result = chain.invoke({
        "current_data": current_data,
        "history": history,
        "input": input_text,
        "langguage": langguage,
    })
    return result


class TestDeepSearchTask(unittest.TestCase):

    def test_case_1_wallet_address(self):
        input_text = "0x980DD1c27614121231F5A64Db9DD7c679C3551d2"
        result = run_deep_search_test(input_text)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["state"], "RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT")
        self.assertEqual(result["data"]["typeList"][0]["type"], 1)

    def test_case_2_project_search(self):
        input_text = "我要查的是 Uniswap"
        result = run_deep_search_test(input_text)
        self.assertIn("Uniswap", result["data"]["typeList"][0]["title"])
        self.assertEqual(result["data"]["typeList"][0]["type"], 4)

    def test_case_3_missing_fields(self):
        input_text = "帮我查一下 Root"
        result = run_deep_search_test(input_text)
        self.assertEqual(result["data"]["state"], "RESEARCH_TASK_DISPLAY_RESEARCH")
        self.assertEqual(result["data"]["typeList"], [])

    def test_case_4_disambiguation(self):
        input_text = "上次你查的是 Uniswap 协议，但我要找的是 Uniswap 的地址"
        result = run_deep_search_test(input_text)
        found = any(t["type"] == 1 for t in result["data"]["typeList"])
        self.assertTrue(found or result["data"]["state"] == "RESEARCH_TASK_DISPLAY_RESEARCH")

    def test_case_5_english_input(self):
        input_text = "SushiSwap"
        result = run_deep_search_test(input_text, langguage="en")
        self.assertEqual(result["data"]["state"], "RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT")
        self.assertTrue(any("SushiSwap" in t["title"] for t in result["data"]["typeList"]))

    def test_case_6_fully_filled(self):
        input_text = "我找的是 Aave 协议，不是 Token，快点开始吧！"
        result = run_deep_search_test(input_text)
        self.assertEqual(result["data"]["state"], "RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT")
        self.assertTrue(any("Aave" in t["title"] for t in result["data"]["typeList"]))

    # 你可以添加更多 case，比如 NFT、机构、Meme Token、模糊提问等

if __name__ == '__main__':
    unittest.main()
