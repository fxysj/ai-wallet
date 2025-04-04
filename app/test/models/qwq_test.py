#通义千问：32B测试
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# 配置 Ollama 本地接口
llm = ChatOpenAI(
    model="qwen:0.5b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # 任意非空字符串
    temperature=0.3,
)

# 调用模型
response = llm.invoke([HumanMessage(content="How many r's are in 'strawberry'?")])
print(response.content)