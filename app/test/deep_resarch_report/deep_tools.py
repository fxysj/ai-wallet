import json
from langchain.tools import Tool
from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory

# 分析函数
def analyze_tokenomics(tokenomics: dict) -> dict:
    price = tokenomics.get("price", 0)
    fdv = tokenomics.get("fdv", 0)
    return {"price": price, "fdv": fdv, "valuation": "High" if fdv > 1e9 else "Low"}

def analyze_contract_security(audit: dict) -> dict:
    issues = audit.get("issues_found", 0)
    return {"issues_found": issues, "security_level": "High Risk" if issues > 5 else "Low Risk"}

def analyze_trading_behavior(trading: dict) -> dict:
    buy_tax = trading.get("buy_tax", 0)
    sell_tax = trading.get("sell_tax", 0)
    return {"total_tax": buy_tax + sell_tax}

# 工具函数包装，输入是字符串形式JSON，输出字符串形式结果
def tokenomics_tool_func(input_str: str) -> str:
    data = json.loads(input_str)
    result = analyze_tokenomics(data)
    return json.dumps(result, ensure_ascii=False)

def contract_security_tool_func(input_str: str) -> str:
    data = json.loads(input_str)
    result = analyze_contract_security(data)
    return json.dumps(result, ensure_ascii=False)

def trading_behavior_tool_func(input_str: str) -> str:
    data = json.loads(input_str)
    result = analyze_trading_behavior(data)
    return json.dumps(result, ensure_ascii=False)

tokenomics_tool = Tool(
    name="TokenomicsAnalyzer",
    func=tokenomics_tool_func,
    description="Analyze tokenomics data in JSON format"
)

contract_security_tool = Tool(
    name="ContractSecurityAnalyzer",
    func=contract_security_tool_func,
    description="Analyze smart contract audit data in JSON format"
)

trading_behavior_tool = Tool(
    name="TradingBehaviorAnalyzer",
    func=trading_behavior_tool_func,
    description="Analyze trading tax and behavior data in JSON format"
)

# 创建 LLM
llm = LLMFactory.getDefaultOPENAI()

# 把所有工具放进tools
tools = [
    tokenomics_tool,
    contract_security_tool,
    trading_behavior_tool,
]

# 创建 React Agent
template = """
你是一个智能分析助理。

用户输入:
{input}

可用工具:
{tools}

工具名称:
{tool_names}

当前对话:
{agent_scratchpad}

请合理调用工具，给出详细分析。
"""

prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template=template,
)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# 输入示例
prompt = f"""
请帮我分析以下数据：

Tokenomics数据: {json.dumps({"price": 1.5, "fdv": 1200000000, "market_cap": 800000000})}
合约安全数据: {json.dumps({"issues_found": 2, "audit_status": "Passed"})}
交易行为数据: {json.dumps({"buy_tax": 2, "sell_tax": 3})}
"""
inputs = {
    "input": prompt,
    "intermediate_steps": [],
    "agent_scratchpad": "",
    "tools": tools,
    "tool_names": [t.name for t in tools],
}
# 调用 Agent
result = agent.invoke(inputs)  # 传入字典，key是 'input'
print(result)
