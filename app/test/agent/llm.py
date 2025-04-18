from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_tavily import TavilySearch

from app.agents.lib.llm.llm import LLMFactory
from app.test.agent.p import DEEPSEARCHTASK_PROMPT_TEST_TOOLS

# 你可以根据需要替换成自己的模型（如 OpenAI, Claude, Groq 等）
llm = LLMFactory.getDefaultOPENAI()  # 比如 ChatOpenAI(model="gpt-4o")
tools = [TavilySearch(max_results=5, topic="general")]
prompt = PromptTemplate(
    template=DEEPSEARCHTASK_PROMPT_TEST_TOOLS,
    input_variables=["current_data", "history", "input", "language", "chain_data"],
)
p = prompt.format(
    current_data=[],
    history=[],
    input="ETH",
    language="cn",
    chain_data=[]
)
# print(p)
agent = LLMFactory.create_custom_agent(llm, tools,prompt=p,debug=True)
# 使用 agent
# 示例 1: invoke
response = agent.invoke({"messages": "ETH"})
print(response["messages"][-1].content)

# 示例 2: stream
# for step in agent.stream(
#     {"messages": "What country hosted Euro 2024?"},
#     stream_mode="values"
# ):
#     step["messages"][-1].pretty_print()