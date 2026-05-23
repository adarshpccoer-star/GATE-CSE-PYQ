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
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain.tools import tool
from IPython.display import Image, display
load_dotenv()



from langchain.tools import tool
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver #memory saver


from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper


@tool
def arxiv_tool(query: str) -> str:
    """
    Search arXiv papers and return summaries.

    Args:
        query: Research topic or paper title
    """

    try:
        arxiv = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(
                top_k_results=2,
                doc_content_chars_max=2000
            )
        )

        result = arxiv.invoke(query)

        if not result:
            return "No papers found."

        return result

    except Exception as e:
        return f"Arxiv search failed: {str(e)}"
@tool 
def add(a:int,b:int)->int:
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
@tool
def multiply(a:int,b:int)->int:
    """
    Multiply two numbers
    Args:
        a: first number
        b: second number
    Returns:
        The product of a and b as integer
    """
    print("Multiplying",a,b)
    return a*b

tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)

# print(arxiv_tool("diffusion models"))
tools=[add,multiply,arxiv_tool,tavily_search_tool]


class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

def llm_response(state:State):
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools = model.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    print({"messages": [response]})
    return {"messages": [response]}


builder = StateGraph(State)

builder.add_node("llm",llm_response)
builder.add_node("tools", ToolNode(tools=tools))

builder.add_edge(START,"llm")
builder.add_conditional_edges("llm", tools_condition)
builder.add_edge("tools", "llm")

memory =MemorySaver()

graph_memory = builder.compile(checkpointer=memory)
display(Image(graph_memory.get_graph().draw_mermaid_png()))

#specify the theard

config = {
"configurable": {"thread_id": "1"},
}
messages = [HumanMessage(content="who won sam altman or elon musk? Also, what is 2+2?")]

messages=graph_memory.invoke({"messages": messages},config=config)
for message in messages["messages"]:
    message.pretty_print()

messages = [HumanMessage(content="now add 200 in it ")]
messages=graph_memory.invoke({"messages": messages},config=config)

for message in messages["messages"]:
    message.pretty_print()
