# 测试无法识别的情况
from langchain_core.output_parsers import JsonOutputParser

from app.agents.lib.llm.llm import LLMFactory
from langchain.prompts import PromptTemplate

from app.agents.proptemts.unclear_prompt_cle import UnClearTemplate


def unclear():
    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        input_variables=["message_history", "latest_message", "attached_data", "langguage"],
        template=UnClearTemplate
    )
    chain = p | llm | JsonOutputParser()

    test_cases = [
        {
            "category": "send",
            "latest_message": "我想给我的朋友转0.5 BTC",
            "expected_response": "Got it. You're looking to send some crypto to someone. Let's proceed with the transfer setup.",
            "intent": "send"
        },
        {
            "category": "receive",
            "latest_message": "请帮我生成一个接收ETH的地址，我需要收款",
            "expected_response": "Got it. You're looking to receive ETH. I will provide you with the necessary address.",
            "intent": "receive"
        },
        {
            "category": "swap",
            "latest_message": "我想从Ethereum链转到BSC链，怎么操作？",
            "expected_response": "Got it. You're looking to swap from Ethereum to Binance Smart Chain. I can help you with the steps.",
            "intent": "swap"
        },
        {
            "category": "buy",
            "latest_message": "我想用人民币买点ETH",
            "expected_response": "Got it. You're looking to buy ETH with CNY. I can guide you through the purchasing process.",
            "intent": "buy"
        },
        {
            "category": "deep_research",
            "latest_message": "我想了解 USDT 的最新发展",
            "expected_response": "Got it. You're interested in the latest development of USDT. I will provide a detailed analysis including its technology, market trends, and potential risks.",
            "intent": "deep_research"
        },
        {
            "category": "account_analysis",
            "latest_message": "请帮我分析一下我的多链资产分布情况",
            "expected_response": "Got it. You're looking to analyze the distribution of your assets across different chains. I can help with that.",
            "intent": "account_analysis"
        },
        {
            "category": "newsletter",
            "latest_message": "我想订阅每日的区块链市场快讯",
            "expected_response": "Got it. You're interested in subscribing to daily blockchain market updates. I will take care of that for you.",
            "intent": "newsletter"
        },
        {
            "category": "unclear",
            "latest_message": "我想要更多的信息但是不太清楚要做什么",
            "expected_response": "Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.",
            "intent": "unclear"
        },
        {
            "category": "unclear",
            "latest_message": "你觉得特朗普怎么看待比特币？",
            "expected_response": "Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.",
            "intent": "unclear"
        }
    ]

    for case in test_cases:
        res = chain.invoke({
            "message_history": "",
            "latest_message": case["latest_message"],
            "attached_data": str({}),
            "langguage": "zh-CN"
        })
        print(f"Category: {case['category']}, Latest Message: {case['latest_message']}")
        print(f"Expected Response: {case['expected_response']}")
        print(f"Generated Response: {res}")
        print("---------------")


def unclear_en():
    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        input_variables=["message_history", "latest_message", "attached_data", "langguage"],
        template=UnClearTemplate
    )
    chain = p | llm | JsonOutputParser()

    test_cases = [
        {
            "category": "send",
            "latest_message": "I want to send 0.5 BTC to my friend",
            "expected_response": "Got it. You're looking to send some crypto to someone. Let's proceed with the transfer setup.",
            "intent": "send"
        },
        {
            "category": "receive",
            "latest_message": "Please help me generate a receiving ETH address, I need to receive funds",
            "expected_response": "Got it. You're looking to receive ETH. I will provide you with the necessary address.",
            "intent": "receive"
        },
        {
            "category": "swap",
            "latest_message": "How do I transfer from Ethereum chain to BSC chain?",
            "expected_response": "Got it. You're looking to swap from Ethereum to Binance Smart Chain. I can help you with the steps.",
            "intent": "swap"
        },
        {
            "category": "buy",
            "latest_message": "I want to buy some ETH using CNY",
            "expected_response": "Got it. You're looking to buy ETH with CNY. I can guide you through the purchasing process.",
            "intent": "buy"
        },
        {
            "category": "deep_research",
            "latest_message": "I want to know about the latest developments of USDT",
            "expected_response": "Got it. You're interested in the latest development of USDT. I will provide a detailed analysis including its technology, market trends, and potential risks.",
            "intent": "deep_research"
        },
        {
            "category": "account_analysis",
            "latest_message": "Please help me analyze my multi-chain asset distribution",
            "expected_response": "Got it. You're looking to analyze the distribution of your assets across different chains. I can help with that.",
            "intent": "account_analysis"
        },
        {
            "category": "newsletter",
            "latest_message": "I want to subscribe to daily blockchain market news",
            "expected_response": "Got it. You're interested in subscribing to daily blockchain market updates. I will take care of that for you.",
            "intent": "newsletter"
        },
        {
            "category": "unclear",
            "latest_message": "I want more information, but I'm not sure what exactly",
            "expected_response": "Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.",
            "intent": "unclear"
        },
        {
            "category": "unclear",
            "latest_message": "What do you think Trump thinks about Bitcoin?",
            "expected_response": "Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.",
            "intent": "unclear"
        }
    ]

    for case in test_cases:
        res = chain.invoke({
            "message_history": "",
            "latest_message": case["latest_message"],
            "attached_data": str({}),
            "langguage": "en"
        })
        print(f"Category: {case['category']}, Latest Message: {case['latest_message']}")
        print(f"Expected Response: {case['expected_response']}")
        print(f"Generated Response: {res}")
        print("---------------")

# Call the function to test
# unclear()


# Call the function to test
if __name__ == '__main__':
    unclear_en()
