from langgraph.graph import StateGraph, START, END
from src.langgraph.state.state import State
from src.langgraph.nodes.basic_chatbot import BasicChatBot

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
        
    def setup_graph(self, usecase: str):
        if not usecase:
            return None
            
        # Normalize the usecase string to avoid casing and whitespace bugs
        clean_usecase = usecase.strip().lower()
        
        if clean_usecase == "basic chatbot":
            return self.basic_chatbot_build_graph()
            
        return None