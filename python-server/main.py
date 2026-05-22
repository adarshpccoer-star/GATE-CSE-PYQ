from langchain_core.messages import AnyMessage
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph.message import add_messages # reducer to add messages without completely removing it
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
load_dotenv()

class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]


def add_tools(a:int,b:int)->int:
    """
    Add two numbers
    Args:
        a: first number
        b: second number
    Returns:
        The sum of a and b as integer
    """
    print("Adding",a,b)
    return a+b

Tools=[add_tools]


def llm_response(state:State):
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools = model.bind_tools(Tools)
    response = llm_with_tools.invoke(state["messages"])
    print({"messages": [response]})
    return {"messages": [response]}

builder = StateGraph(State)

builder.add_node("llm",llm_response)
builder.add_node("tools", ToolNode(tools=Tools))


builder.add_edge(START,"llm")
builder.add_conditional_edges("llm", tools_condition)
builder.add_edge("tools", "llm")
graph = builder.compile()

# Invoke the graph
response_state = graph.invoke({"messages": [HumanMessage(content="what is life and 2+2")]})
# Extract the list of messages from the final state dictionary and print them
for message in response_state["messages"]:
    message.pretty_print()
