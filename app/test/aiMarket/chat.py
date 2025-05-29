import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_tavily import TavilySearch
from openai import max_retries

from app.agents.lib.llm.llm import LLMFactory
from app.test.aiMarket.Web3Context import Web3Context
from app.test.aiMarket.tools import toolsPrompt


def context():
    return  {
  "id": "type3_unicorn",
  "title": "Analysis report of the Unicorn",
  "logo": "",
  "type": 3,
  "detail": "Unicorn 是一种基于 Base 链的代币，当前市值约为 11.8 亿人民币，24 小时交易量约为 1.64 亿人民币。",
  "chain_id": 8453,
  "contract_addresses": ["0x9a54...9DcadB"],
  "symbol": "UNI"
}

tools = [TavilySearch(max_retries=2)]

def Ai():
    llm = LLMFactory.getDefaultOPENAI()
    #llm = llm.bind_tools(tools=tools)

    web3ContextToolPrompet = PromptTemplate(
        template= toolsPrompt,
        input_variables=["context"]
    )

    chain = web3ContextToolPrompet| llm.with_structured_output(Web3Context)
    result = chain.invoke({"context": json.dumps(context(), ensure_ascii=False)})
    print(result)



if __name__ == '__main__':
    Ai()

