from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SocialInfo:
    twitter: Optional[str]
    telegram: Optional[str]
    discord: Optional[str]
    github: Optional[str]
    website: Optional[str]

@dataclass
class Tokenomics:
    price: str
    fdv: str
    market_cap: str
    max_supply: str
    circulating_supply: str
    holders: int
    top10_holders_ratio: str
    locked_ratio: str
    burn_ratio: str
    unlock_schedule: Optional[str]

@dataclass
class ContractAudit:
    audit_status: str  # e.g. "Audited", "Not Audited"
    audit_firm: Optional[str]
    issues_found: Optional[int]
    high_risk_issues: Optional[int]
    proxy_used: bool
    upgradable: bool
    owner_address: str
    creator_address: str

@dataclass
class TradingAnalysis:
    buy_tax: str
    sell_tax: str
    slippage: str
    anti_bot: bool
    honeypot: bool
    tx_limit: Optional[str]
    whale_protection: bool

@dataclass
class DexLiquidityInfo:
    dex_name: str
    pair_address: str
    liquidity_usd: str
    token0: str
    token1: str
    lp_locked: bool
    lock_duration: Optional[str]

@dataclass
class CommunityStats:
    twitter_followers: int
    telegram_members: int
    discord_members: int
    github_commits_past_30d: int
    dev_active: bool

@dataclass
class OnChainStats:
    daily_active_users: int
    contract_invocations_24h: int
    gas_usage_rank: Optional[int]
    whale_interactions: int

@dataclass
class RiskAssessment:
    risk_score: float  # 0 ~ 10
    tags: List[str]  # e.g., ["High Buy Tax", "Proxy Contract", "Whale Risk"]
    investment_suggestion: str

@dataclass
class Web3TokenReport:
    project_name: str
    symbol: str
    chain_id: int
    contract_address: str
    description: str
    social_info: SocialInfo
    tokenomics: Tokenomics
    contract_audit: ContractAudit
    trading_analysis: TradingAnalysis
    dex_liquidity: List[DexLiquidityInfo]
    community_stats: CommunityStats
    onchain_stats: OnChainStats
    risk_assessment: RiskAssessment
    report_generated_at: str  # ISO 8601 timestamp



PRO= """
你是一个专业的加密资产分析师，请基于以下信息撰写一份完整的深度研究报告，内容包括但不限于：项目基本介绍、代币经济模型、链上数据概览、安全风险分析、流动性分布、潜在风险点和投资者须知，并在最后提供简明扼要的投资建议
以下是 一份完整的研究报告 的最新数据：
{{report}}

"""
P = PromptTemplate(
    template=PRO,
    input_variables=["report"],
)
re = [
    {
        "success": True,
        "promptedAction": [
            "RESEARCH_SAVE",
            "RESEARCH_SHARE",
            "RESEARCH_BUY_TOKEN"
        ],
        "data": {
            "intent": "deep_research",
            "form": {
                "selectedType": {
                    "id": "type3_baby-doge-coin",
                    "title": "Analysis report of the Baby Doge Coin",
                    "logo": "",
                    "type": 3,
                    "detail": "Baby Doge Coin is a meme cryptocurrency designed to be deflationary and more scarce over time. Holders earn more tokens automatically through a 5% fee from every on-chain transaction within the Baby Doge ecosystem. The token is available on multiple blockchain networks, including BNB Smart Chain, Ethereum, and Solana.",
                    "chain_id": 56,
                    "contract_addresses": [
                        "0xc748673057861a797275cd8a068abb95a902e8de"
                    ],
                    "symbol": "BabyDoge"
                }
            },
            "timestamp": 1748247826.61698,
            "description": "I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": {
                "basicInfo": {
                    "Token_Price": "0.0(8)168",
                    "FDV": "0.00",
                    "M.Cap": "278.64M",
                    "Max_Supply": "0.00",
                    "Circulation": "165004395.75B",
                    "Token_Symbol": "BabyDoge",
                    "Contract_Address": [
                        "0xc748673057861a797275cd8a068abb95a902e8de"
                    ],
                    "Contract_Creator": "0xf1***062b74",
                    "Contract_Owner": "0x00***000000",
                    "Toker_Holders": "1898788",
                    "Token_Supply": "334102151269745958.14",
                    "Top10_Holders_Ratio": "80.00%",
                    "AttentionItem": 0,
                    "RiskyItem": 0
                }
            },
            "details": {
                "basicInfo": {
                    "Token_Price": "0.0(8)168",
                    "FDV": "0.00",
                    "M.Cap": "278.64M",
                    "Max_Supply": "0.00",
                    "Circulation": "165004395.75B",
                    "Token_Symbol": "BabyDoge",
                    "Contract_Address": [
                        "0xc748673057861a797275cd8a068abb95a902e8de"
                    ],
                    "Contract_Creator": "0xf1***062b74",
                    "Contract_Owner": "0x00***000000",
                    "Toker_Holders": "1898788",
                    "Token_Supply": "334102151269745958.14",
                    "Top10_Holders_Ratio": "80.00%",
                    "AttentionItem": 0,
                    "RiskyItem": 10
                },
                "contractSecurity": [
                    {
                        "title": "Contract Source Code Verified",
                        "description": "This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets",
                        "value": "1"
                    },
                    {
                        "title": "No Proxy",
                        "description": "There is no proxy in the contract. The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.",
                        "value": "0"
                    },
                    {
                        "title": "No Mint Function",
                        "description": "Mint function is transparent or non-existent. Hidden mint functions may increase the amount of tokens in circulation and effect the price of the token.",
                        "value": "0"
                    },
                    {
                        "title": "No Function Found That Retrieves Ownership",
                        "description": "If this function exists, it is possible for the project owner to regain ownership even after relinquishing it",
                        "value": "0"
                    },
                    {
                        "title": "No Hidden Owner",
                        "description": "No hidden owner address was found for the token. For contract with a hidden owner, developer can still manipulate the contract even if the ownership has been abandoned.",
                        "value": "0"
                    },
                    {
                        "title": "This Token Can Not Self Destruct",
                        "description": "No self-destruct function found. If this function exists and is triggered, the contract will be destroyed, all functions will be unavailable, and all related assets will be erased.",
                        "value": "0"
                    },
                    {
                        "title": "No External Call Risk found",
                        "description": "External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.",
                        "value": "0"
                    }
                ],
                "honeypotRisk": {
                    "Buy_Tax": "0.00%",
                    "Sell_Tax": "0.00%",
                    "description": "Above 10% may be considered a high tax rate. More than 50% tax rate means may not be tradable.",
                    "list": [
                        {
                            "title": "This Does Not Appear To Be A Honeypot",
                            "description": "We are not aware of any malicious code.",
                            "value": "0"
                        },
                        {
                            "title": "NO Codes Found To Suspend Trading",
                            "description": "If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk).",
                            "value": "0"
                        },
                        {
                            "title": "No Trading Cooldown Function",
                            "description": "The token contract has no trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.",
                            "value": "0"
                        },
                        {
                            "title": "Anti-Whale Mechanism Exists (Limited Number Of Transactions)",
                            "description": "There is a limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).",
                            "value": "1"
                        },
                        {
                            "title": "Anti Whale Can  Be Modified",
                            "description": "The maximum trading amount or maximum position can  be modified.",
                            "value": "1"
                        },
                        {
                            "title": "NO Blacklist",
                            "description": "The blacklist function is not included. If there is a blacklist, some addresses may not be able to trade normally (honeypot risk).",
                            "value": "0"
                        },
                        {
                            "title": "Whitelist Function",
                            "description": "Having a whitelist function means that, for this contract, some privileged users may have greater advantages in transactions, such as bypassing transaction limits, being exempt from taxes, trading earlier than others, or not being affected by transaction cooldown restrictions.",
                            "value": "1"
                        },
                        {
                            "title": "Tax Cannot Be Modified",
                            "description": "The contract owner may not contain the authority to modify the transaction tax. If the transaction tax is increased to more than 49%, the tokens will not be able to be traded (honeypot risk).",
                            "value": "1"
                        },
                        {
                            "title": "No Tax Changes For Personal Addresses",
                            "description": "No tax changes were found for every assigned address.If it exists, the contract owner may set a very outrageous tax rate for assigned address to block it from trading.",
                            "value": "1"
                        }
                    ]
                },
                "dexAndLiquidity": [
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "8.70M",
                        "pair": "0xc736ca3d...8b3d4e0ee0"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "6.20M",
                        "pair": "0x61db764c...d85a4cef5f"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "13.30K",
                        "pair": "0xbf7cd39d...5955c9381b"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "3.88K",
                        "pair": "0xbed24d19...d4e99f9c1f"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "1.88K",
                        "pair": "0xcf25533b...d15c6620e5"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "1.52K",
                        "pair": "0xbf958db5...d55e2155a6"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "444.96",
                        "pair": "0xed3f52c4...2cb4ca45f5"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "45.88",
                        "pair": "0x573419ff...b0e1a81a93"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Ape",
                        "liquidity": "15.36",
                        "pair": "0x7d6c5f94...aa3fa1c053"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "2.88",
                        "pair": "0x411cb17c...9fe8b0d81b"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "0.35",
                        "pair": "0x9864efa2...f745f428a4"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "0.01",
                        "pair": "0xf5e3de54...e210624d9c"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "0.01",
                        "pair": "0x6d32c53f...be40ea7381"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "0.01",
                        "pair": "0x94c4831a...c1230ceeee"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "0.00",
                        "pair": "0xf2de996e...474543b6c5"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "0.00",
                        "pair": "0x59b471b0...a7ce21e48c"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "ThenaV2",
                        "liquidity": "0.00",
                        "pair": "0x7a7c5b69...e235b75033"
                    }
                ]
            },
            "state": "RESEARCH_TASK_DISPLAY_RESEARCH",
            "type": 3
        },
        "message": "ok",
        "confidence": 99.9,
        "alternatives": []
    }
]

llm = LLMFactory.getDefaultOPENAI().with_structured_output(Web3TokenReport)
chain = P | llm
response = chain.invoke({"report": re})
print(response)