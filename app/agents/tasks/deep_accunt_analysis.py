#深度账号交易分析
import json
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.deep_account_asnis_form_prompt_en import AccountASNYC_PROPMT
from app.agents.schemas import AgentState, Intention


async def analysis_task(state: AgentState) -> AgentState:
    print("analysis_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=AccountASNYC_PROPMT,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    chain = prompt | llm | JsonOutputParser()

    print("================history:=============")
    print(state.history)
    print("================history:=============")
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage
    })
    response_data = chain_response
    print("response_data")
    print(response_data)
    data = response_data.get("data")
    if data is None:
      data = {}

    data["intent"] = Intention.account_analysis.value
    if data:
        form = data.get("form")
        if form:
          missField = data.get("missFields")
          # 这里进行分析
          if missField:
            return state.copy(update={"result": data})
        else:
          #否则的话要进行清空
          data["missFields"] = []
          data["description"] = "Congratulations, all the information is complete! Deep analysis is about to begin!"
          data["state"] = "ANALYSIS_TASK_DISPLAY_ANALYSIS"

    data["overview"] = getMockData()["overview"]
    data["achievements"] = getMockData()["achievements"]
    data["details"] = getMockData()["details"]
    data["socialShareOptions"] = getMockData()["socialShareOptions"]
    return state.copy(update={"result": data})

def getMockData():
    return {
  "intent": "account_analysis",
  "state": "Pending",
  "form": {
    "userId": "0x1234567890abcdef",
    "walletAddress": "0xabcdef1234567890"
  },
  "missingFields": [
    {
      "field": "age",
      "reason": "Missing user age information"
    }
  ],
  "overview": {
    "totalBalance": {
      "value": "50000.00",
      "trend": 12.5,
      "comparisonPercentile": 75
    },
    "accountHealth": {
      "score": 85,
      "grade": "A",
      "riskProfile": "moderate",
      "diversificationScore": 72
    },
    "activitySnapshot": {
      "level": "active",
      "accountAge": {
        "days": 730,
        "percentile": 50
      },
      "weeklyTransactions": 25,
      "blockchainsUsed": ["Ethereum", "Polygon", "Solana"]
    }
  },
  "achievements": [
    {
      "id": "achievement_1",
      "title": "Early Adopter",
      "description": "You joined in the early days of the project.",
      "unlockedAt": "2023-01-15T10:00:00Z",
      "rarity": "legendary",
      "icon": "https://example.com/icons/achievement_early_adopter.png",
      "socialShareImage": "https://example.com/images/share_early_adopter.png"
    },
    {
      "id": "achievement_2",
      "title": "DeFi Expert",
      "description": "You have completed 100 DeFi transactions.",
      "unlockedAt": "2024-02-10T14:30:00Z",
      "rarity": "epic",
      "icon": "https://example.com/icons/achievement_defi_expert.png"
    }
  ],
  "details": {
    "tokenHoldings": [
      {
        "token": "ETH",
        "symbol": "ETH",
        "logo": "https://example.com/icons/eth_logo.png",
        "balance": "50.00",
        "value": "80000.00",
        "allocation": "40%",
        "performance": {
          "percentChange24h": 5.2,
          "percentChange7d": 10.5,
          "entryPosition": "mid"
        },
        "riskLevel": "medium",
        "tooltip": "Ethereum is a leading smart contract platform."
      },
      {
        "token": "SOL",
        "symbol": "SOL",
        "logo": "https://example.com/icons/sol_logo.png",
        "balance": "200.00",
        "value": "4000.00",
        "allocation": "10%",
        "performance": {
          "percentChange24h": -1.8,
          "percentChange7d": 3.0,
          "entryPosition": "early"
        },
        "riskLevel": "high"
      }
    ],
    "transactionHistory": {
      "count": 150,
      "frequency": "daily",
      "gasSavings": "15% savings on gas fees",
      "mostUsedDApps": [
        {
          "name": "Uniswap",
          "logo": "https://example.com/icons/uniswap_logo.png",
          "usageCount": 50,
          "category": "DeFi"
        },
        {
          "name": "OpenSea",
          "logo": "https://example.com/icons/opensea_logo.png",
          "usageCount": 30,
          "category": "NFT"
        }
      ],
      "recentTransactions": [
        {
          "hash": "0xabcdef1234567890abcdef",
          "type": "swap",
          "description": "Swapped 1 ETH for 50 DAI",
          "value": "2000.00",
          "timestamp": "2024-03-10T15:00:00Z",
          "gasUsed": "0.01 ETH"
        },
        {
          "hash": "0x9876543210abcdef987654",
          "type": "stake",
          "description": "Staked 10 SOL in Solana pool",
          "value": "500.00",
          "timestamp": "2024-03-08T12:30:00Z",
          "gasUsed": "0.005 SOL"
        }
      ]
    },
    "nextLevelGoals": [
      {
        "id": "goal_1",
        "title": "Complete 100 DeFi Transactions",
        "description": "Complete 100 more DeFi transactions to level up.",
        "difficulty": "intermediate",
        "progress": 45,
        "reward": "500 DAI",
        "steps": [
          {
            "label": "Start with Uniswap",
            "completed": True
          },
          {
            "label": "Stake tokens on Aave",
            "completed": False,
            "tooltip": "Stake a minimum of 50 tokens."
          }
        ]
      }
    ],
    "insights": [
      {
        "title": "Consider Diversifying Your Portfolio",
        "description": "You have a high concentration in Ethereum. Consider diversifying into other assets.",
        "iconType": "tip",
        "actionable": True,
        "actionText": "View token options",
        "actionUrl": "https://example.com/diversify"
      },
      {
        "title": "Gas Fees Could Be Lowered",
        "description": "You could save up to 15% on gas fees by using more efficient networks like Polygon.",
        "iconType": "warning",
        "actionable": False
      }
    ]
  },
  "socialShareOptions": {
    "portfolioCard": "https://example.com/share/portfolio_card",
    "achievementCards": [
      "https://example.com/share/achievement_card_early_adopter",
      "https://example.com/share/achievement_card_defi_expert"
    ],
    "accountAgeCard": "https://example.com/share/account_age_card",
    "customText": "Check out my blockchain portfolio and achievements!"
  }
}
if __name__ == '__main__':
    res = getMockData()
    print(res)