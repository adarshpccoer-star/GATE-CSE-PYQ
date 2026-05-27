from langchain_core.messages import AIMessage

class BasicChatBot:
    def __init__(self, model):
        self.llm = model

    def process(self, state: dict) -> dict:
        # 1. Safely extract messages
        messages_list = state.get('messages', [])
        
        # 2. Defensive check to ensure we aren't passing empty inputs to the model
        if not messages_list:
            raise ValueError("Node Processing Error: 'messages' state key is empty or missing!")

        # 3. Invoke LLM safely
        try:
            response = self.llm.invoke(messages_list)
        except Exception as e:
            raise RuntimeError(f"LLM Invocation failed inside node: {e}")
            
        # 4. If the model returns None, create a fallback AIMessage to prevent state crash
        if response is None:
            response = AIMessage(content="Error: The LLM returned an empty response.")

        return {"messages": [response]}