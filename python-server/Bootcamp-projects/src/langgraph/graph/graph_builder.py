from langgraph.graph import StateGraph,START,END
from src.langgraph.state.state import State
from src.langgraph.nodes.basic_chatbot import BasicChatbot
class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        
        self.basic_chatbot = BasicChatbot(self.llm)

        self.graph_builder.add_node("chatbot", self.basic_chatbot.process )
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)
        
    def setup_graph(self,usecase:str):
        if usecase == "Basic ChatBot":
            self.basic_chatbot_build_graph()