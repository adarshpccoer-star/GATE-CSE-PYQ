import streamlit as st
from src.langgraph.ui.streamlit.loadui import LoadStreamlitUI  # Adjust paths to match your folder structure
from src.langgraph.llms.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder
from src.langgraph.ui.streamlit.display_result import DisplayResultStreamlit

def main():
    # 1. Render Sidebar and Fetch User Settings
    
    ui_loader = LoadStreamlitUI()
    user_controls = ui_loader.load_streamlit_ui()
    
    usecase = user_controls.get("select_usecase")
    
    # 2. Initialize the LLM Provider
    llm_provider = GroqLLM(user_controls)
    llm = llm_provider.get_llm_model()
    
    # 3. Build the Compiled Graph
    builder = GraphBuilder(llm)
    compiled_graph = builder.setup_graph(usecase)
    
    if compiled_graph is None:
        st.info("Please select a valid usecase from the sidebar to initialize the AI Graph.")
        return

    # 4. Handle Main Chat Input
    user_query = st.chat_input("Ask me anything...")
    
    if user_query:
        # 5. Route and stream results directly to the UI
        display_handler = DisplayResultStreamlit(
            usecase=usecase, 
            graph=compiled_graph, 
            user_message=user_query
        )
        display_handler.display_result_on_ui()

if __name__ == "__main__":
    main()