import sys
import importlib
import streamlit as st

# Force python to discard the old cache of display_result if it exists
if "src.langgraph.ui.streamlit.display_result" in sys.modules:
    importlib.reload(sys.modules["src.langgraph.ui.streamlit.display_result"])

# Now safely import your modules
from src.langgraph.ui.streamlit.loadui import LoadStreamlitUI
from src.langgraph.llms.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder
from src.langgraph.ui.streamlit.display_result import DisplayResultStreamlit

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
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
            
            if not model:
                st.error("Error: Failed to initialize LLM model.")
                return
                
            raw_usecase = user_input.get("select_usecase")
            
            if not raw_usecase:
                st.error("Error: Please select a valid usecase from the sidebar.")
                return
            
            # Normalize string once globally to immunize against space/casing bugs
            usecase = raw_usecase.strip().lower()
            
            graph_builder = GraphBuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase)
                if graph is None:
                    st.error(f"Error: Graph compilation failed. Unrecognized usecase: '{raw_usecase}'")
                    return
                
                # Instantiating and executing the visualizer
                display = DisplayResultStreamlit(usecase, graph, user_message)
                display.display_result_on_ui()
                
            except Exception as e:
                st.error(f"Error building or executing graph: {e}")
                return
            
        except Exception as e:
            st.error(f"Configuration Error: {e}")
            return

if __name__ == "__main__":
    load_langgraph_ui()