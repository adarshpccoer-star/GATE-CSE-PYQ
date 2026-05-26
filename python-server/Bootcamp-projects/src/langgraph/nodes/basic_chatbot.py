from src.langgraph.state.state import State

class BasicChatBotNode:
    def __init__(self,model):
        self.llm=model

    def process(self,state:State)->dict:

        return {"message":self.llm.invoke(state['messages'])}