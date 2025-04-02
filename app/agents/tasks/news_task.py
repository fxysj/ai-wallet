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
            "title": "Ethereum's Shanghai Upgrade Brings Major Improvements",
            "summary": "Ethereum's Shanghai upgrade has successfully launched, improving scalability and reducing gas fees.",
            "url": "https://example.com/ethereum-shanghai-upgrade",
            "source": "Blockchain News Daily",
            "published": "2025-04-01"
        },
        {
            "title": "Bitcoin Hits New All-Time High Amid Institutional Adoption",
            "summary": "Bitcoin has reached a new all-time high, driven by increasing institutional investment and growing mainstream acceptance.",
            "url": "https://example.com/bitcoin-all-time-high",
            "source": "Crypto Times",
            "published": "2025-03-28"
        },
        {
            "title": "DeFi Security: Latest Trends and Risks in 2025",
            "summary": "A new report highlights the latest security threats in DeFi, including smart contract vulnerabilities and phishing attacks.",
            "url": "https://example.com/defi-security-trends",
            "source": "DeFi Insights",
            "published": "2025-03-25"
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