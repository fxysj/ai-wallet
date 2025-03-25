from typing import Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.swap_task_propmt import SWAPTASK_TEMPLATE


class SwapTransactionSchema(BaseModel):
    from_: str = Field(..., alias="from", description="兑换来源资产（格式: 链.代币，例如 'BSC.BNB'）")
    to: str = Field(..., description="兑换目标资产（格式: 链.代币，例如 'AVAX_CCHAIN.USDT'）")
    amount: float = Field(..., description="兑换数量")


def cross_chain_swap(addreess: str, to: str, amount: float):
    """
    获取最佳的跨链兑换路径
    """
    try:
        print(f"Finding best route from {addreess} to {to} with amount {amount}")

        return {
            "routes": [
                {
                    "estimatedDuration": "2 minutes",
                    "fee": "0.1%",
                    "expectedOutput": amount * 0.999,
                    "steps": [
                        f"Step 1: Bridge from {addreess.split('.')[0]} to {to.split('.')[0]}",
                        "Step 2: Swap on DEX"
                    ]
                }
            ]
        }
    except Exception as e:
        return {
            "error_type": "ROUTING_ERROR",
            "error_message": f"Failed to get route: {str(e)}"
        }

cross_chain_tool = StructuredTool.from_function(
    name="cross_chain_tool",
    func=cross_chain_swap,
    description="Find the best route for swapping tokens.",
    args_schema=SwapTransactionSchema
)
if __name__ == '__main__':
    test_input = {
        "history": "",
        "input": "我想用 BSC.BNB 兑换 10 个 AVAX_CCHAIN.USDT.E",
        "current_data": [],
        "langguage": "zh"
    }

    prompt = PromptTemplate(
        template=SWAPTASK_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI().bind_tools([cross_chain_tool])
    # 使用新版输出解析器
    # 如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = chain.invoke(test_input)
    print(chain_response)

