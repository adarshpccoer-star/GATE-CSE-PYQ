import streamlit as st
from langchain_core.messages import HumanMessage

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        if self.usecase == "basic chatbot":
            with st.chat_message("user"):
                st.write(self.user_message)
            
            # Stream the graph state
            for event in self.graph.stream({"messages": [HumanMessage(content=self.user_message)]}):
                for value in event.values():
                    # Check for our plural 'messages' key
                    if 'messages' in value and value['messages']:
                        # Grab the last message appended to the state (the AI's reply)
                        last_message = value['messages'][-1]
                        with st.chat_message("assistant"):
                            st.write(last_message.content)