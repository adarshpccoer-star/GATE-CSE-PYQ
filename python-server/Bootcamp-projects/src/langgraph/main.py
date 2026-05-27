import streamlit as st
from src.langgraph.ui.streamlit.loadui import LoadStreamlitUI 
from src.langgraph.llms.groqllm import GroqLLM
from src.langgraph.graph.graph_builder import GraphBuilder
from src.langgraph.ui.streamlit.display_result import DisplayResultStreamlit

def main():
    # 1. Render Sidebar and Fetch User Settings (Handles page config internally)
    ui_loader = LoadStreamlitUI()
    user_input = ui_loader.load_streamlit_ui()
    
    if not user_input:
        st.error("Error loading user configuration. Please check your sidebar settings.")
        return
    
    user_controls = user_input.get("user_controls")
    usecase = user_input.get("usecase")

    if not usecase:
        st.info("Please select a valid use-case from the sidebar to initialize the AI Graph.")
        return

    # 2. Handle Main Chat Input
    user_query = st.chat_input("Ask me anything...")
    
    # Check if the "AI News" sidebar run action happened instead of regular chat
    if usecase == "AI News" and st.session_state.get("IsFetchButtonClicked", False):
        user_query = st.session_state.get("TimeFrame", "Daily")
        st.session_state.IsFetchButtonClicked = False  # Reset flag

    if user_query:
        try:
            # 3. Initialize the LLM Provider
            llm_provider = GroqLLM(user_controls)
            llm = llm_provider.get_llm_model()
            
            # 4. Build the Compiled Graph
            builder = GraphBuilder(llm)
            compiled_graph = builder.setup_graph(usecase)
            
            if compiled_graph is None:
                st.error(f"Failed to compile graph for use-case: '{usecase}'")
                return

            # 5. Route and stream results directly to the UI
            display_handler = DisplayResultStreamlit(
                usecase=usecase, 
                graph=compiled_graph, 
                user_message=user_query
            )
            display_handler.display_result_on_ui()
            
        except Exception as e:
            st.error(f"An error occurred during execution: {str(e)}")

if __name__ == "__main__":
    main()