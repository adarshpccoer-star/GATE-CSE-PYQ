from langgraph.graph import StateGraph, START, END
from src.langgraph.state.state import State
from src.langgraph.nodes.basic_chatbot import BasicChatBot
from src.langgraph.tools.search_tools import get_tools ,create_tool_node
from langgraph.prebuilt import tools_condition,ToolNode
from src.langgraph.nodes.chat_with_tool import ChatBotWithTools
from src.langgraph.nodes.ai_news_node import AINewsNode


class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        self.basic_chatbot = BasicChatBot(self.llm)
        self.graph_builder.add_node("chatbot", self.basic_chatbot.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        return self.graph_builder.compile()


    def chatbot_with_tools_build_graph(self):
        tools=get_tools()
        tool_node=create_tool_node(tools)
        chatbot_instance = ChatBotWithTools(self.llm)

        llm = self.llm
        self.graph_builder.add_node("chatbot", chatbot_instance.process) 
        self.graph_builder.add_node("tools", tool_node)

        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition,"tools")
        self.graph_builder.add_edge("tools", "chatbot")
        return self.graph_builder.compile()



    def ai_news_builder_graph(self):
        ai_news_node = AINewsNode(self.llm)
        self.graph_builder.add_node("fetch_news", ai_news_node.fetch_news)
        self.graph_builder.add_node("summarise_news", ai_news_node.summarize_news)
        self.graph_builder.add_node("save_results", ai_news_node.save_result)

        self.graph_builder.add_edge(START, "fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarise_news")
        self.graph_builder.add_edge("summarise_news", "save_results")
        self.graph_builder.add_edge( "save_results",END)
        return self.graph_builder.compile()
    
     
    def setup_graph(self, usecase: str):
        if not usecase:
            return None
            
        
        clean_usecase = usecase.strip()
        
        if clean_usecase == "basic chatbot":
            return self.basic_chatbot_build_graph()
        if clean_usecase == "chatbot with web":
            return self.chatbot_with_tools_build_graph()
            
        if clean_usecase == "AI News":
            return self.ai_news_builder_graph()            
        return None
    