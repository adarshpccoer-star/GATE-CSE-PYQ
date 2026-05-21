from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages # reducer to add messages without completely removing it
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
load_dotenv()

class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

def llm_response(state:State):
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    response = model.invoke(state["messages"])
    # 2. Return a dictionary updating the 'messages' key
    return {"messages": [response]}

builder = StateGraph(State)

builder.add_node("llm",llm_response)

builder.add_edge(START,"llm")
builder.add_edge("llm",END)

graph = builder.compile()

# Invoke the graph
response_state = graph.invoke({"messages": "what is 2+2"})

# Extract the list of messages from the final state dictionary and print them
for message in response_state["messages"]:
    message.pretty_print()