#新闻资讯任务处理器
import json
import time

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic.v1 import BaseModel
from typing_extensions import TypedDict, List

from app.agents.lib.llm.llm import LLMFactory
from app.agents.lib.redisManger.redisManager import RedisDictManager
from app.agents.proptemts.news_form_prompt_en import NEWS_TEMPLATE
from app.agents.proptemts.news_search_test import NEWS_SEARCH_PROMPT
from app.agents.schemas import AgentState, Intention
from langchain_tavily import TavilySearch
from langchain.tools import tool
class Article(TypedDict):
    title: str  # 文章标题
    summary: str  # 文章摘要或内容简述
    url: str  # 文章的原始链接
    source: str  # 新闻来源，比如媒体名称
    published: str  # 发布时间，格式为 YYYY-MM-DD

class Articles(BaseModel):
    articles: List[Article] #文章列表

@tool(args_schema=Articles)
def return_articles(articles: List[Article]):
    """模型在完成搜索后调用此工具，将结果结构化返回"""
    return {"articles": articles}



#根据类型进行搜索
def getNewSearch(timeframe:str):
    try:
        redis = RedisDictManager()
        response = redis.get("news_" + timeframe)
        if response:
            return response

        llm = LLMFactory.getDefaultOPENAI()
        prompt = PromptTemplate(
            template="""你是新闻助手，只调用一次 TavilySearch 工具检索区块链新闻，然后返回文章列表。
            关键词：{input}
            要包含如下:
            class Article(TypedDict):
            title: str  # 文章标题
            summary: str  # 文章摘要或内容简述
            url: str  # 文章的原始链接
            source: str  # 新闻来源，比如媒体名称
            published: str  # 发布时间，格式为 YYYY-MM-DD
            {agent_scratchpad}""",
            input_variables=["input", "agent_scratchpad"],
        )
        tools = [TavilySearch(max_retries=2)]
        agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
        # 包装为 AgentExecutor 后才能调用 invoke
        executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=3, max_execution_time=30,
                                 return_intermediate_steps=False)
        result = executor.invoke({"input": timeframe})
        output = result["output"]
        p = PromptTemplate(
            template="""
                上下文{context}
                根即上下文内容提取信息 返回结果如下 严格按照JSON返回
                ```json
                  [
          {{
            "title": "标题",
            "summary": "简要内容",
            "source": "信息来源",
            "url": "新闻链接",
            "published": "发布日期（YYYY-MM-DD）"
          }}
        ]
                ```
                """,
            input_variables=["context"],
        )
        c = p | LLMFactory.getDefaultOPENAI() | JsonOutputParser()
        response = c.invoke({"context": output})
        redis.add("news_" + timeframe, response)
        return response
    except Exception:
        return newsLetter([])
    finally:
        return newsLetter([])






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
    data["intent"] = Intention.newsletter.value
    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
    # 获取对应的
    missField = data["missFields"]
    if missField:
        return state.copy(update={"result": data})
    data["newsletter"] = newsLetter(state.attached_data)
    return state.copy(update={"result": data})

if __name__ == '__main__':
    article: Article = {
        "title": "Mastercard Develops Crypto Payment Network",
        "summary": "Mastercard is building a blockchain-based network to facilitate digital asset transactions among consumers, merchants, and financial institutions, aiming to replicate its card network's scale in the crypto space.",
        "url": "https://www.businessinsider.com/mastercard-building-venmo-crypto-blockchain-digital-assets-2025-3",
        "source": "Business Insider",
        "published": "2025-03-31"
    }