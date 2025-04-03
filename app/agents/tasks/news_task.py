#新闻资讯任务处理器
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.news_form_prompt import NEWS_TEMPLATE
from app.agents.schemas import AgentState


def newsLetter(attached_data):
    return [
    {
        "title": "Mastercard Develops Crypto Payment Network",
        "summary": "Mastercard is building a blockchain-based network to facilitate digital asset transactions among consumers, merchants, and financial institutions, aiming to replicate its card network's scale in the crypto space.",
        "url": "https://www.businessinsider.com/mastercard-building-venmo-crypto-blockchain-digital-assets-2025-3",
        "source": "Business Insider",
        "published": "2025-03-31"
    },
    {
        "title": "French State Bank Bpifrance to Invest in Cryptocurrencies",
        "summary": "Bpifrance plans to allocate up to €25 million to purchase lesser-known cryptocurrencies, supporting French crypto enterprises and demonstrating France's commitment to becoming a leader in crypto technologies.",
        "url": "https://www.reuters.com/business/finance/french-state-bank-bpifrance-builds-fund-buy-cryptocurrencies-2025-03-27/",
        "source": "Reuters",
        "published": "2025-03-27"
    },
    {
        "title": "FDIC Removes Barrier for Banks' Crypto Activities",
        "summary": "The FDIC has rescinded a prior requirement for banks to obtain approval before engaging in crypto-related activities, facilitating greater integration of cryptocurrencies into traditional financial institutions.",
        "url": "https://www.barrons.com/articles/crypto-banks-fdic-d04d06cc",
        "source": "Barron's",
        "published": "2025-03-28"
    },
    {
        "title": "Wyoming Tests State-Backed Stablecoin",
        "summary": "Wyoming has initiated testing of its state-backed stablecoin, WYST, on multiple blockchains, marking a significant step as one of the first U.S. state governments to launch a stablecoin.",
        "url": "https://www.axios.com/2025/03/27/stablecoin-wyoming-blockchains-fidelity-paypal",
        "source": "Axios",
        "published": "2025-03-27"
    },
    {
        "title": "Axis Bank and J.P. Morgan Enable 24/7 Dollar Payments",
        "summary": "India's Axis Bank, in partnership with J.P. Morgan, has introduced real-time U.S. dollar payments for commercial clients, enhancing cross-border payment efficiency.",
        "url": "https://www.reuters.com/business/finance/indias-axis-bank-jp-morgan-roll-out-anytime-dollar-payments-clients-2025-03-27/",
        "source": "Reuters",
        "published": "2025-03-27"
    }
]

async def news_task(state: AgentState) -> AgentState:
    print("news_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=NEWS_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage
    })
    print(chain_response)
    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
    data["newsletter"] = newsLetter(state.attached_data)
    return state.copy(update={"result": data})