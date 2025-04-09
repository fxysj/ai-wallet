INTENT_PROMPT_TEMPLATE = """
Based on the historical conversation records (up to 5 messages):
{message_history}

Classify the user's latest request intent:
Latest message content: {latest_message}
Attached data: {attached_data}

Please choose the most appropriate category from the following (return EXACTLY one value):
- send: The user plans to send cryptocurrency to another address
- receive: The user plans to receive cryptocurrency
- swap: Exchange different cryptocurrencies
- buy: Purchase cryptocurrency with fiat currency
- deep_research: Requires deep research in the cryptocurrency field
- account_analysis: Analyze wallet assets
- newsletter: Get cryptocurrency market updates
- unclear: Unable to clearly classify

Please strictly return the lowercase category value, without including any other content.

Here are examples:
Example:
 - **User Input**: `transfer` / `I want to transfer` / `I want to send 300 USDT to a friend`
  - **AI Response**: send
- **User Input**: `I want to receive` / `I want to receive 200 USDT`
  - **AI Response**: receive
- **User Input**: `cross-chain`
  - **AI Response**: swap
- **User Input**: `buy`
  - **AI Response**: buy
"""
