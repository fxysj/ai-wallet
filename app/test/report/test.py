from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.deep_search_sumary import DEEP_SEARCH_SUMARY_TMEP
report = [
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
                    "type": 3,
                    "chain_id": 1,
                    "contract_addresses": [
                        "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
                    ],
                    "symbol": "SHIB"
                }
            },
            "timestamp": 1747123566.3695908,
            "description": "I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": {
                "tokenPrice": "0.00",
                "fdv": "9.05B",
                "m.cap": "9.04B",
                "maxSupply": "589552.70B",
                "circulation": "589249.89B",
                "tokenSymbol": "SHIB",
                "contractAddress": [
                    "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
                ],
                "contractCreator": "0xb8***0dfa08",
                "contractOwner": "--",
                "tokerHolders": "1506320",
                "tokenSupply": "620163107977989.01",
                "top10HoldersRatio": "62.00"
            },
            "details": {
                "tokenPrice": "0.00",
                "fdv": "9.05B",
                "m.cap": "9.04B",
                "maxSupply": "589552.70B",
                "circulation": "589249.89B",
                "tokenSymbol": "SHIB",
                "contractAddress": [
                    "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
                ],
                "contractCreator": "0xb8***0dfa08",
                "contractOwner": "--",
                "tokerHolders": "1506320",
                "tokenSupply": "620163107977989.01",
                "top10HoldersRatio": "62.00",
                "contractSourceCodeVerified": {
                    "title": "Contract source code verified",
                    "description": "This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets",
                    "value": "1"
                },
                "noProxy": {
                    "title": "No proxy",
                    "description": "There is no proxy in the contract. The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.",
                    "value": "0"
                },
                "noMintFunction": {
                    "title": "No mint function",
                    "description": "Mint function is transparent or non-existent. Hidden mint functions may increase the amount of tokens in circulation and effect the price of the token.",
                    "value": "0"
                },
                "noFunctionFoundThatRetrievesOwnership": {
                    "title": "No function found that retrieves ownership",
                    "description": "If this function exists, it is possible for the project owner to regain ownership even after relinquishing it",
                    "value": "0"
                },
                "ownerCantChangeBalance": {
                    "title": "Owner can't change balance",
                    "description": "The contract owner is not found to have the authority to modify the balance of tokens at other addresses.",
                    "value": "0"
                },
                "noHiddenOwner": {
                    "title": "No hidden owner",
                    "description": "No hidden owner address was found for the token. For contract with a hidden owner, developer can still manipulate the contract even if the ownership has been abandoned.",
                    "value": "0"
                },
                "thisTokenCanNotSelfDestruct": {
                    "title": "This token can not self destruct",
                    "description": "No self-destruct function found. If this function exists and is triggered, the contract will be destroyed, all functions will be unavailable, and all related assets will be erased.",
                    "value": "0"
                },
                "noExternalCallRiskFound": {
                    "title": "No external call risk found",
                    "description": "External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.",
                    "value": "0"
                },
                "thisTokenIsNotAGasAbuser": "--",
                "buyTax": "0.00%",
                "sellTax": "0.00%",
                "thisDoesNotAppearToBeAHoneypot": {
                    "title": "This does not appear to be a honeypot",
                    "description": "We are not aware of any malicious code.",
                    "value": "0"
                },
                "noCodesFoundToSuspendTrading": {
                    "title": "No codes found to suspend trading",
                    "description": "If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk).",
                    "value": "0"
                },
                "noTradingCooldownFunction": {
                    "title": "No trading cooldown function",
                    "description": "The token contract has no trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.",
                    "value": "0"
                },
                "noAntiWhaleUnlimitedNumberOfTransactions": {
                    "title": "No anti_whale(Unlimited number of transactions)",
                    "description": "There is no limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).",
                    "value": "0"
                },
                "antiWhaleCannotBeModified": {
                    "title": "Anti whale can not be modified",
                    "description": "The maximum trading amount or maximum position can not be modified",
                    "value": "0"
                },
                "taxCannotBeModified": "--",
                "noBlacklist": {
                    "title": "No blacklist",
                    "description": "The blacklist function is not included. If there is a blacklist, some addresses may not be able to trade normally (honeypot risk).",
                    "value": "0"
                },
                "noWhitelist": {
                    "title": "No whitelist",
                    "description": "The whitelist function is not included. If there is a whitelist, some addresses may not be able to trade normally (honeypot risk).",
                    "value": "0"
                },
                "noTaxChangesFoundForPersonalAddresses": "--",
                "dexAndLiquidity": [
                    {
                        "liquidity_type": "UniV2",
                        "name": "UniswapV2",
                        "liquidity": "506633.90642969",
                        "pair": "0x811beed0119b4afce20d2583eb608c6f7af1954f"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "457034.71187557849621514755",
                        "pair": "0x2f62f2b4c5fcd7570a709dec05d68ea19c82a9ec"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "123118.38533237740623433755",
                        "pair": "0x5764a6f2212d502bc5970f9f129ffcd61e5d7563"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "44650.41217178420337272730",
                        "pair": "0xe07c687cecb3caf246ded3240d186181d5eae705"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "16241.42850113383385155152",
                        "pair": "0x94e4b2e24523cf9b3e631a6943c346df9687c723"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "UniswapV2",
                        "liquidity": "5705.26731852",
                        "pair": "0x773dd321873fe70553acc295b1b49a104d968cc8"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "2747.670269648470",
                        "pair": "0xa15cc73e881c06d8db06b50b7a3688b763c18350"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "2664.603449517100",
                        "pair": "0xb0cc75ed5aabb0acce7cbf0302531bb260d259c4"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "SushiSwapV2",
                        "liquidity": "2009.29827463",
                        "pair": "0x24d3dd4a62e29770cf98810b09f89d3a90279e7a"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "203.855402288380",
                        "pair": "0xe9131a276fd07af729b5537a429346e8affc67e0"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "UniswapV2",
                        "liquidity": "92.96631907",
                        "pair": "0x881d5c98866a08f90a6f60e3f94f0e461093d049"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "SushiSwapV2",
                        "liquidity": "1.75440163",
                        "pair": "0xb011ea8096ce5986f3e89b4c2c02f193c82abea8"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "UniswapV2",
                        "liquidity": "0.00000012",
                        "pair": "0x4e6e41306c7ef6e53ecdb34e3155c73fcb7869f3"
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
if __name__ == '__main__':

    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        template=DEEP_SEARCH_SUMARY_TMEP,
        input_variables=["report"]
    )
    c = p | llm|JsonOutputParser()
    print(c.invoke({"report": report}))
