from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    news_data: list
    frequency: str
    summary: str
    filename: str