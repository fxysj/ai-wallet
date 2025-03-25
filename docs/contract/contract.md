### 大模型和前端交互约定

## 路由规定

### 统一的接口

- **地址**: `/api/v1`

---

## 前端的格式

```json
{
  "session_id": "用户的会话信息 JwtToken为主",
  "messages": [
    {"role": "user", "content": "转账", "data": {}},
    {"role": "system", "content": "你需要办理的是什么转账的业务?", "data": {}},
    {"role": "user", "content": "我要向0x1113 进行转入 3个ETH", "data": {}},
    {
      "role": "system",
      "content": "ok 我明白您的意思啦 您的意思是希望向0x113这个地址进行转入3个ETH类型的对吧?",
      "Success": true,
      "message": "ok",
      "promentNexttAction": [],
      "intent": "send",
      "data": {
        "state": "完成",
        "form": {
          "chainIndex": "ETH",
          "fromAddr": "",
          "toAddr": "0x113",
          "txAmount": "3",
          "tokenSymbol": "",
          "tokenAddress": "",
          "extJson": ""
        },
        "missFields": [{"name": "chainIndex", "description": "区块链索引"}],
        "DxTransActionDetail": {}
      }
    }
  ]
}
```

---

## 转账完整请求

```json
{
  "session_id": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
  "messages": [
    {"role": "user", "content": "转账", "data": {}},
    {"role": "system", "content": "你需要办理的是什么转账的业务?", "data": {}},
    {"role": "user", "content": "我要向0x1113 进行转入 3个ETH", "data": {}},
    {
      "role": "system",
      "content": "ok 我明白您的意思啦 您的意思是希望向0x113这个地址进行转入3个ETH类型的对吧?",
      "Success": true,
      "message": "ok",
      "promentNexttAction": [],
      "data": {
        "intent": "send",
        "state": "完成",
        "form": {
          "chainIndex": "ETH",
          "fromAddr": "",
          "toAddr": "0x113",
          "txAmount": "3",
          "tokenSymbol": "",
          "tokenAddress": "",
          "extJson": ""
        },
        "missFields": [
          {"name": "chainIndex", "description": "区块链索引"}
        ],
        "DxTransActionDetail": {}
      }
    }
  ]
}
```
```
智能体监控地址:
https://smith.langchain.com/o/b875d8b3-251a-504d-a542-97343661b0ea/projects/p/79f2c255-0de0-483c-aadd-9693a82f64bd?timeModel=%7B%22duration%22%3A%227d%22%7D&peek=996054dd-b151-4bcd-8366-bd39ff661177

```
