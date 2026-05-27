from src.langgraph.tools.search_tools import get_tools
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from src.langgraph.state.state import State
from langchain_core.prompts import ChatPromptTemplate

class ChatBotWithTools:
    def __init__(self, model):
        # 1. bind_tools returns a new instance; assign it to self.llm
        self.llm = model.bind_tools(get_tools())
    
    def process(self, state:  dict) -> dict:
        try:
            messages_list = state.get('messages', [])
            if not messages_list:
                raise ValueError("Node Processing Error: 'messages' state key is empty or missing!")

            # 2. Add a placeholder so the prompt knows where to insert the history
            prompt_template = ChatPromptTemplate([
                ("system", "You are a helpful AI bot which also has access to tools."),
                ("placeholder", "{messages}")
            ])

            # 3. Form a clean chain pipeline without trailing variables
            chain = prompt_template | self.llm
            
            # 4. Invoke the chain using a dictionary matching your placeholder key
            response = chain.invoke({"messages": messages_list})
            
        except Exception as e:
            raise RuntimeError(f"LLM Invocation failed inside node: {e}")
            
        if response is None:
            response = AIMessage(content="Error: The LLM returned an empty response.")
            
        return {"messages": [response]}