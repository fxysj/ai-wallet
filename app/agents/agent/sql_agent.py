from langchain.agents import AgentExecutor
from langchain_core.language_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from app.agents.agent_tools.agent_record_tools import (
    GetAgentRecordTool,
    QueryAgentRecordsTool,
    ExportAgentRecordsCSVTool,
    ExportAgentRecordsExcelTool
)
from app.agents.lib.llm.llm import LLMFactory
from app.db.agent_record_model import AgentRecord


def get_sql_agent(llm: BaseChatModel = None) -> AgentExecutor:
    if llm is None:
        llm = LLMFactory.getDefaultOPENAI()

    tools = [
        GetAgentRecordTool(),
        QueryAgentRecordsTool(),
        ExportAgentRecordsCSVTool(),
        ExportAgentRecordsExcelTool()
    ]
    agent = create_react_agent(
        model=llm,
        tools=tools,
        response_format=AgentRecord
    )
    return agent
