from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

# LangGraph 闭环作为子工具注册
from main import run_sentiment_loop

def run_sentiment_agent_tool(input: str) -> str:
    # 从用户输入中抽取评论列表（示例：你可以用 NLP 模块提取）
    comments = input.split(";")  # 简单分隔演示
    user_id = "user-001"
    result = run_sentiment_loop(comments, user_id)
    return result["final_result"]

tools = [
    Tool(
        name="SentimentFeedbackLoop",
        func=run_sentiment_agent_tool,
        description="分析用户评论的情绪并提供优化建议。输入是用分号分隔的评论内容"
    )
]

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# 多轮对话交互
print(agent.run("帮我分析这些评论：I love this!; This sucks; Amazing experience; Terrible service"))
