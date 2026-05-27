import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        # 1. Always display the user's input message first
        with st.chat_message("user"):
            st.write(self.user_message)
            
        # 2. Setup the initial state payload
        inputs = {"messages": [HumanMessage(content=self.user_message)]}
        
        # 3. Stream the graph executions
        # Using stream_mode="updates" allows us to watch node completions clearly
        for event in self.graph.stream(inputs, stream_mode="updates"):
            for node_name, value in event.items():
                # Check if the node returned messages
                if 'messages' in value and value['messages']:
                    last_message = value['messages'][-1]
                    
                    # Only print to UI if it's an AIMessage with actual content
                    # (This filters out ToolMessages or tool-call initiation frames)
                    if isinstance(last_message, AIMessage) and last_message.content:
                        with st.chat_message("assistant"):
                            st.write(last_message.content)