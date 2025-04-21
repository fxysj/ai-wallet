

###当用户选择对应的项目类型请求:
请求地址:{{url}}/api/v1/chat
请求方式:POST 
请求Body:json:
```
{
    "id": "HxFZ2BIL2hwW2E6z1113",
    "messages": [
        {
            "role": "user",
            "content": "帮我查一下 SHIB",
            "data": {
                "intent": "deep_research",
                "state": "RESEARCH_TASK_DISPLAY_RESEARCH",
                "selectedType": {
                    "id": 117,
                    "type": 2,
                    "chain_id": 1,
                    "contract_addresses": [
                        "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"
                    ],
                    "symbol": "SHIB"
                }
            }
        }
    ],
    "session_id": "0x22223"
}
```
响应如下（类型为 项目/VC Token):
overview:卡片的信息
details:详细信息
type:类型 2,4(2:项目 4:VC Token)
详情参考:https://97d3iw.axshare.com/?g=14&id=drayln&p=%E6%B7%B1%E5%BA%A6%E5%88%86%E6%9E%90%E6%A8%A1%E5%9E%8Bagent___&sc=3
ROWDATA:https://www.rootdata.com/zh/Api/Doc
[
    {
        "success": true,
        "promptedAction": [
            "RESEARCH_SAVE",
            "RESEARCH_SHARE",
            "RESEARCH_BUY_TOKEN"
        ],
        "data": {
            "intent": "deep_research",
            "state": "RESEARCH_TASK_DISPLAY_RESEARCH",
            "selectedType": {
                "id": 117,
                "type": 2,
                "chain_id": 1,
                "contract_addresses": [
                    "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"
                ],
                "symbol": "SHIB"
            },
            "timestamp": 1744970148.2828474,
            "description": "I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": {
                "Project_Name": "Solana",
                "logo": "https://public.rootdata.com/images/b15/1666364340995.jpg",
                "Token_Symbol": "SOL",
                "Token_Price": "",
                "FDV": "",
                "M.Cap": "",
                "Brief": "High performance underlying blockchain",
                "Fundraising_Amount": 335760000,
                "Ecosystem": "",
                "X_Followers": "",
                "Descroption": "Solana is a high-performance blockchain protocol designed to enable scalable, user-friendly applications for the world."
            },
            "details": {
                "Project_Name": "Solana",
                "logo": "https://public.rootdata.com/images/b15/1666364340995.jpg",
                "Token_Symbol": "SOL",
                "Token_Price": "",
                "FDV": "",
                "M.Cap": "",
                "Brief": "High performance underlying blockchain",
                "Fundraising_Amount": 335760000,
                "Ecosystem": "",
                "X_Followers": "",
                "Descroption": "Solana is a high-performance blockchain protocol designed to enable scalable, user-friendly applications for the world.",
                "Reports": [],
                "Events": [],
                "investors": [
                    {
                        "invest_id": 146,
                        "name": "Polychain",
                        "logo": "https://public.rootdata.com/images/b11/1666594345259.jpg",
                        "type": 2,
                        "lead_investor": 1
                    },
                    {
                        "invest_id": 237,
                        "name": "Andreessen Horowitz",
                        "logo": "https://public.rootdata.com/images/b30/1684378189698.jpg",
                        "type": 2,
                        "lead_investor": 1
                    },
                    {
                        "invest_id": 154,
                        "name": "Multicoin Capital",
                        "logo": "https://public.rootdata.com/images/b11/1666595811200.jpg",
                        "type": 2,
                        "lead_investor": 1
                    },
                    {
                        "invest_id": 4095,
                        "name": "CoinShares",
                        "logo": "https://public.rootdata.com/images/b16/1666708223779.jpg",
                        "type": 1,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 127,
                        "name": "Slow Ventures",
                        "logo": "https://public.rootdata.com/images/b17/1666771674014.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 154,
                        "name": "Multicoin Capital",
                        "logo": "https://public.rootdata.com/images/b11/1666595811200.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 205,
                        "name": "Distributed Global",
                        "logo": "https://public.rootdata.com/images/b17/1666777126677.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 622,
                        "name": "BlockTower Capital",
                        "logo": "https://public.rootdata.com/images/b17/1666872618399.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 10666,
                        "name": "500 Global",
                        "logo": "https://public.rootdata.com/images/b16/1668833547965.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 10940,
                        "name": "Passport Capital",
                        "logo": "https://public.rootdata.com/images/b16/1668916747073.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 8942,
                        "name": "Chris McCann",
                        "logo": "https://public.rootdata.com/images/b19/1668693102065.jpg",
                        "type": 3,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 4176,
                        "name": "Alameda Research",
                        "logo": "https://public.rootdata.com/images/b6/1668583230756.jpg",
                        "type": 1,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 132,
                        "name": "Ryze Labs",
                        "logo": "https://public.rootdata.com/images/b6/1694083345119.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 153,
                        "name": "NGC Ventures",
                        "logo": "https://public.rootdata.com/images/b17/1666772406262.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 221,
                        "name": "CMS Holdings",
                        "logo": "https://public.rootdata.com/images/b17/1666777767934.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 257,
                        "name": "Blockchange Ventures",
                        "logo": "https://public.rootdata.com/images/b17/1666778988873.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 10595,
                        "name": "Foundation Capital",
                        "logo": "https://public.rootdata.com/images/b16/1668786932521.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 10939,
                        "name": "Rockaway Ventures",
                        "logo": "https://public.rootdata.com/images/b16/1668916651826.jpg",
                        "type": 2,
                        "lead_investor": 0
                    },
                    {
                        "invest_id": 11295,
                        "name": "Jump Trading",
                        "logo": "https://public.rootdata.com/images/b22/1668495942205.jpg",
                        "type": 2,
                        "lead_investor": 0
                    }
                ],
                "Team_Member": [],
                "Social_Media": {
                    "website": "https://solana.com/",
                    "github": "https://github.com/solana-labs",
                    "gitbook": "",
                    "X": "https://x.com/solana",
                    "cmc": "5426",
                    "linkedin": "https://www.linkedin.com/company/solanalabs/",
                    "medium": "https://medium.com/solana-labs",
                    "defillama": "https://defillama.com/chain/Solana"
                }
            },
            "type": 2
        },
        "message": "ok",
        "confidence": 99.9,
        "alternatives": []
    }
]
###当用户输入查询关键词:
请求地址:{{url}}/api/v1/chat
请求方式:POST 
请求Body:json: