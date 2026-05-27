from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

def get_tools():

    tools=[ TavilySearch(
    max_results=1,
    topic="general",)
   ]

    return tools

def create_tool_node(tools):
    
    return ToolNode(tools=tools)