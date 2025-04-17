import sqlite3
import requests
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import PromptTemplate
from openai import api_key
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
def get_engine_for_chinook_db():
    with open("Chinook_Sqlite.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

engine = get_engine_for_chinook_db()

db = SQLDatabase(engine)

from langchain.chat_models import init_chat_model
from app.config import settings
llm = init_chat_model("gpt-4o-mini", model_provider="openai",api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_API_BASE_URL)
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# print(toolkit.get_tools())

from langchain import hub
# https://smith.langchain.com/hub

# prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
with open("offcie.md", "r", encoding="utf-8") as f:
    template = f.read()
# assert len(prompt_template.messages) == 1
# print(prompt_template.input_variables)
prompt_template = PromptTemplate(
    input_variables=["dialect", "top_k", "input"],
    template=template,
)
system_message = prompt_template.format(dialect="SQLite", top_k=5,input="{input}")
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=system_message)

example_query = "Which country's customers spent the most?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


example_query = "Who are the top 3 best selling artists?"
events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()

# 1. Iron Maiden - 140 sales
# 2. U2 - 107 sales
# 3. Metallica - 91 sales