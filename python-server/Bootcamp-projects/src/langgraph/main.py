import streamlit as st
from src.langgraph.ui.streamlit.loadui import LoadStreamlitUI
from src.langgraph.llms.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder
def load_langgraph_ui():

    # Load sidebar/UI controls
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    # Validate UI load
    if user_input is None:
        st.error("Error: Failed to load user input from UI")
        return

    # Chat input section
    user_message = st.chat_input("Enter your message here")

    if user_message:
        try:
            obj_llm_config  = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
            if not model:
                st.error("error")
            usecase = user_input.get("selected_usecase")
            
            if not usecase:
                st.error("error")
                return
            
            graph_builder = GraphBuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase)
            except Exception as e:
                st.error(f"error",{e})
                return
            
        except Exception as e:
            st.error(f"error",{e})
            return

        
    