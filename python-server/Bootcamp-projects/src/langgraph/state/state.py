from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Annotated tells LangGraph to use add_messages to append new data 
    # instead of overwriting it with None
    messages: Annotated[list, add_messages]