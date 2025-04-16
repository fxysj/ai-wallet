from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.agent import AgentAction, AgentFinish
from typing import Dict, Any
from app.config import settings

# ✅ 回调类
class ReasoningTraceHandler(BaseCallbackHandler):
    def __init__(self, initial_state: Dict[str, Any]):
        self.state = initial_state
        self.state["reasoning_trace"] = []

    def on_agent_action(self, action: AgentAction, **kwargs):
        self.state["reasoning_trace"].append({
            "thought": action.log.strip() if action.log else "No log",
            "action": action.tool,
            "action_input": action.tool_input
        })

    def on_tool_end(self, output: str, **kwargs):
        if self.state["reasoning_trace"]:
            self.state["reasoning_trace"][-1]["observation"] = output

    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        self.state["reasoning_trace"].append({
            "thought": finish.log.strip() if finish.log else "No finish log",
            "final_answer": finish.return_values.get("output")
        })

# ✅ 封装 LLM
def getOpenAI(open_key: str, url: str) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        openai_api_key=open_key,
        openai_api_base=url,
    )

# ✅ 示例工具
def weather_tool_func(location: str) -> str:
    return f"{location}今天天气晴，25度。"

weather_tool = Tool(
    name="WeatherTool",
    func=weather_tool_func,
    description="用于查询天气信息，输入是地名"
)

# ✅ 构造 Agent
def get_reasoning_agent(llm, tools, initial_state):
    callbacks = [ReasoningTraceHandler(initial_state)]
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        callbacks=callbacks
    )
    return agent

# ✅ 实际运行
if __name__ == "__main__":
    initial_state = {}
    llm = getOpenAI(settings.OPENAI_API_KEY, settings.OPENAI_API_BASE_URL)
    agent = get_reasoning_agent(llm, [weather_tool], initial_state)

    question = "北京今天天气怎么样？"
    result = agent.invoke({"input": question})

    print("\n最终回答:", result)
    print("\n推理轨迹:")
    from pprint import pprint
    pprint(initial_state["reasoning_trace"])
