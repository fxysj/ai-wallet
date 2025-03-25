# 意图分类专用提示词
INTENT_PROMPT_TEMPLATE = """
基于历史对话记录（最多5条）：
{message_history}

分类用户最新请求的意图：
最新消息内容：{latest_message}
附加数据：{attached_data}

请从以下类别选择最匹配的（返回EXACTLY一个值）：
- send: 用户计划向其他地址发送加密资产
- receive: 用户计划接收加密资产
- swap: 兑换不同加密货币
- buy: 用法币购买加密货币
- deep_research: 需要加密领域的深度研究
- account_analysis: 分析钱包资产
- newsletter: 获取加密市场动态
- unclear: 无法明确分类

请严格返回小写的类别值，不要包含其他内容。

下面是案例:
Example:
 - **用户输入**：`转账` / `我要转账` / `我要给朋友转 300 USDT`
  - **AI 响应**  send
- **用户输入**：`我要收款` / `我要收 200 USDT`
  - **AI 响应**  receive
- **用户输入**：`跨链`
  - **AI 响应**  swap
- **用户输入**：`购买`
  - **AI 响应**  buy
"""
