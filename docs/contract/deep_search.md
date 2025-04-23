

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
            "form": {
                "query": "查询狗狗币",
                "selectedType": {
                    "type": 3,
                    "chain_id": 56,
                    "contract_addresses": [
                        "0xba2ae424d960c26247dd6c32edc70b295c744c43"
                    ],
                    "symbol": "SHIB"
                }
            },
            "timestamp": 1745375636.6305938,
            "description": "I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": {
                "tokenPrice": "0.00",
                "fdv": "8.07B",
                "m.cap": "8.07B",
                "maxSupply": "589552.70B",
                "circulation": "589250.37B",
                "tokenSymbol": "DOGE",
                "contractAddress": [
                    "0xba2ae424d960c26247dd6c32edc70b295c744c43"
                ],
                "contractCreator": "0x08***e5b9b7",
                "contractOwner": "--",
                "tokerHolders": "938310",
                "tokenSupply": "1702329929.01",
                "top10HoldersRatio": "66.00"
            },
            "details": {
                "tokenPrice": "0.00",
                "fdv": "8.07B",
                "m.cap": "8.07B",
                "maxSupply": "589552.70B",
                "circulation": "589250.37B",
                "tokenSymbol": "DOGE",
                "contractAddress": [
                    "0xba2ae424d960c26247dd6c32edc70b295c744c43"
                ],
                "contractCreator": "0x08***e5b9b7",
                "contractOwner": "--",
                "tokerHolders": "938310",
                "tokenSupply": "1702329929.01",
                "top10HoldersRatio": "66.00",
                "contractSourceCodeVerified": {
                    "title": "Contract source code verified",
                    "description": "This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets",
                    "value": "1"
                },
                "noProxy": {
                    "title": "In this contract, there is a proxy contract.",
                    "description": "The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.",
                    "value": "1"
                },
                "noMintFunction": "--",
                "noFunctionFoundThatRetrievesOwnership": "--",
                "ownerCantChangeBalance": "--",
                "noHiddenOwner": "--",
                "thisTokenCanNotSelfDestruct": "--",
                "noExternalCallRiskFound": "--",
                "thisTokenIsNotAGasAbuser": "--",
                "buyTax": "0.00%",
                "sellTax": "0.00%",
                "thisDoesNotAppearToBeAHoneypot": {
                    "title": "This does not appear to be a honeypot",
                    "description": "We are not aware of any malicious code.",
                    "value": "0"
                },
                "noCodesFoundToSuspendTrading": "--",
                "noTradingCooldownFunction": "--",
                "noAntiWhaleUnlimitedNumberOfTransactions": "--",
                "antiWhaleCannotBeModified": "--",
                "taxCannotBeModified": "--",
                "noBlacklist": "--",
                "noWhitelist": "--",
                "noTaxChangesFoundForPersonalAddresses": "--",
                "dexAndLiquidity": [
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "571726.26654335",
                        "pair": "0xac109c8025f272414fd9e2faa805a583708a017f"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "354832.87416889902265910455",
                        "pair": "0xce6160bb594fc055c943f59de92cee30b8c6b32c"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "75054.97722822",
                        "pair": "0x1ef315fa08e0e1b116d97e3dfe0af292ed8b7f02"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "47291.20654377595321009765",
                        "pair": "0x3319a81a316abd4c086f7048904e31ff86648b38"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "43280.584932937094132083694",
                        "pair": "0x89da4102853c6cf3f4e9979cbb1dc4a166f38e84"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "ThenaV3",
                        "liquidity": "30936.12558873588626414000",
                        "pair": "0xff4840a06708e53b620e2670295265029fa72a78"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Ape",
                        "liquidity": "30586.49613247",
                        "pair": "0xfd1ef328a17a8e8eeaf7e4ea1ed8a108e1f2d096"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "27040.42610687",
                        "pair": "0x0fa119e6a12e3540c2412f9eda0221ffd16a7934"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "17754.06368250",
                        "pair": "0xf8e9b725e0de8a9546916861c2904b0eb8805b96"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "14302.1361502221449749930",
                        "pair": "0x023b6298e2f9ae728b324757599f2a36e002a55a"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV1",
                        "liquidity": "10239.23385433",
                        "pair": "0x1efcb446bfa553a2eb2fff99c9f76962be6ecac3"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "2330.09601101",
                        "pair": "0xe27859308ae2424506d1ac7bf5bcb92d6a73e211"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV1",
                        "liquidity": "2234.03367482",
                        "pair": "0x4adb22473e8dbf5efd0bf554ae35d7f3c5178fc5"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "907.81884370799506133884",
                        "pair": "0xc2710fe8191bb171973ac0c85c21f935c0efcbc6"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "868.33117150",
                        "pair": "0xa1d7621adadb86c83779b94d978c48760f5dce67"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "UniswapV3",
                        "liquidity": "643.253854845576105570277594",
                        "pair": "0xde3dff2ee6dbe835cb8c014060f2854582e9a8f1"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV1",
                        "liquidity": "398.23534656",
                        "pair": "0xa3b12f16e0c1f8362acb243e0e98cf672c49b046"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "151.12971081",
                        "pair": "0x9a307fe3f4057d4552d9efdf16fe3ea1353ed64c"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "47.08461969795146181545",
                        "pair": "0xd777cb8471d06835846c80246a42580483e1a0c5"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "8.16848250",
                        "pair": "0x714ac16cf8ad30485a7a6f30e41ab93ea45146af"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV1",
                        "liquidity": "1.95299505",
                        "pair": "0x083f89062de9a2fcc5a0211f6a7c9ed87a5b2c3e"
                    },
                    {
                        "liquidity_type": "UniV3",
                        "name": "PancakeV3",
                        "liquidity": "0.783066046107704628269",
                        "pair": "0x3a367f21ca2fc0fda84f3af6eb174c6d834e0ba3"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "0.35584749",
                        "pair": "0x3eb4d745db8e167758475375ad3f2033f6a8332f"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Ape",
                        "liquidity": "0.27535632",
                        "pair": "0xc5feaf5ca55b406697f32b4a2811d2670582b821"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "0.25630585",
                        "pair": "0xc17555705c3bdc8ec3e0d33dc9bbe78a36fffac2"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Ape",
                        "liquidity": "0.14656094",
                        "pair": "0x2eda0071f10b71b5c63eccd7a582f864dbfec387"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "Biswap",
                        "liquidity": "0.05056867",
                        "pair": "0x9edefcda125b5157f3447ce708106fab7429867a"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "PancakeV2",
                        "liquidity": "0.00439598",
                        "pair": "0x764d72c0cc82b4b6365e1db72c827b9ca0faca2c"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "0.00000642",
                        "pair": "0xa005261dbd2b9b973f5d4628025a63d0a76ef4be"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "ThenaV2",
                        "liquidity": "0.00000026",
                        "pair": "0x37487428a2cff3e21f9d9452b4f6759cc23e4805"
                    },
                    {
                        "liquidity_type": "UniV2",
                        "name": "mdex",
                        "liquidity": "0.00000000",
                        "pair": "0x9458692d0c15190537682066a470fbb32383d226"
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

```
