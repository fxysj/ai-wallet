from typing import Dict
from pydantic import BaseModel, Field
from langchain.tools import tool

class SwapTransactionSchema(BaseModel):
    from_: str = Field(..., alias="from", description="兑换来源资产（格式: 链.代币，例如 'BSC.BNB'）")
    to: str = Field(..., description="兑换目标资产（格式: 链.代币，例如 'AVAX_CCHAIN.USDT'）")
    amount: float = Field(..., description="兑换数量")

@tool(
    name_or_callable="cross_chain_swap",
    description="获取最佳跨链兑换路径。输入需要包含来源资产、目标资产和兑换数量",
    args_schema=SwapTransactionSchema
)
async def cross_chain_swap(params: SwapTransactionSchema) -> Dict:
    """
    执行跨链兑换路径查找的工具函数

    Args:
        params: 包含兑换信息的参数对象

    Returns:
        包含兑换路径信息的字典，或者错误信息
    """
    try:
        # 模拟调用跨链API
        print(f"Finding best route from {params.from_} to {params.to} with amount {params.amount}")

        return {
            "routes": [
                {
                    "estimatedDuration": "2 minutes",
                    "fee": "0.1%",
                    "expectedOutput": params.amount * 0.999,
                    "steps": [
                        f"Step 1: Bridge from {params.from_.split('.')[0]} to {params.to.split('.')[0]}",
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
