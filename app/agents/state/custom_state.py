from typing_extensions import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep


class CustomState(TypedDict):
    today: str
    messages: Annotated[list[BaseMessage], add_messages]
    is_last_step: IsLastStep