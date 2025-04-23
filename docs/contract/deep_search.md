

###当用户选择对应的项目类型请求:
请求地址:{{url}}/api/v1/chat 选中类型为2,4 2项目  4 VCTOKEN 
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
    'projectName': 'Solana',
    'logo': 'https://public.rootdata.com/images/b15/1666364340995.jpg',
    'tokenSymbol': 'SOL',
    'tokenPrice': '',
    'fdv': '',
    'mCap': '',
    'brief': 'High performance underlying blockchain',
    'fundraisingAmount': 335760000,
    'ecosystem': '',
    'xFollowers': '',
    'description': 'Solana is a high-performance blockchain protocol designed to enable scalable, user-friendly applications for the world.'
},
            "details": {
  "projectName": "Solana",
  "logo": "https://public.rootdata.com/images/b15/1666364340995.jpg",
  "tokenSymbol": "SOL",
  "tokenPrice": "",
  "fdv": "",
  "mCap": "",
  "brief": "High performance underlying blockchain",
  "fundraisingAmount": 335760000,
  "ecosystem": "",
  "xFollowers": "",
  "descroption": "Solana is a high-performance blockchain protocol designed to enable scalable, user-friendly applications for the world.",
  "reports": [],
  "events": [],
  "investors": [
    {
      "investId": 146,
      "name": "Polychain",
      "logo": "https://public.rootdata.com/images/b11/1666594345259.jpg",
      "type": 2,
      "leadInvestor": 1
    },
    {
      "investId": 237,
      "name": "Andreessen Horowitz",
      "logo": "https://public.rootdata.com/images/b30/1684378189698.jpg",
      "type": 2,
      "leadInvestor": 1
    }
  ],
  "teamMember": [],
  "socialMedia": {
    "website": "https://solana.com/",
    "github": "https://github.com/solana-labs",
    "gitbook": "",
    "x": "https://x.com/solana",
    "cmc": "5426",
    "linkedin": "https://www.linkedin.com/company/solanalabs/",
    "medium": "https://medium.com/solana-labs",
    "defillama": "https://defillama.com/chain/Solana"
  }
}
            ,
            "type": 2
        },
        "message": "ok",
        "confidence": 99.9,
        "alternatives": []
    }
]
###当用户输入查询关键词: 选中的类型为 3 MEMETOKEN 
请求地址:{{url}}/api/v1/chat
请求方式:POST 
请求Body:json:
```
{
    "id": "HxFZ2BIL2hwW2E6z1113",
    "messages": [
        {
            "role": "user",
            "content": "查询狗狗币",
            "data": {
                "intent":"deep_research",
                "form":{
                    "query":"查询狗狗币",
                    "selectedType":{
                        "type":3,
                        "chain_id":56,
                        "contract_addresses":["0xba2ae424d960c26247dd6c32edc70b295c744c43"],
                        "symbol":"SHIB"
                    }
                }
            }
        }
    ],
    "session_id": "0x22223"
}
```
返回如下:
```json

```
