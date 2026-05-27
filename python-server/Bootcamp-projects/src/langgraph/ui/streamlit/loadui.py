import streamlit as st
from src.langgraph.ui.uiconfigfile import Config
import os

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(
            page_title="LangGraph Orchestrator",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.header(f"🤖 {self.config.get_page_title()}")

        with st.sidebar:
            st.title("Settings")

            # 1. LLM Selection
            llm_options = self.config.get_llm_options()
            self.user_controls["select_llm"] = st.selectbox(
                "Select LLM Provider",
                llm_options
            )

            # 2. GROQ Section
            if self.user_controls["select_llm"] == "GROQ":
                st.subheader("GROQ Configuration")
                self.user_controls["select_groq_model"] = st.selectbox(
                    "Select GROQ Model",
                    self.config.get_groq_model_options()
                )

                self.user_controls["GROQ_API_KEY"] = st.text_input(
                    "Enter GROQ API Key",
                    type="password",
                    placeholder="gsk_..."
                )

                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("Please enter your GROQ API Key")

            # 3. Use Case Selection
            usecase_options = self.config.get_usecase_options()
            selected_usecase = st.selectbox(
                "Select Use Case",
                usecase_options
            )
            self.user_controls["select_usecase"] = selected_usecase

            # 4. Tool Integration (Tavily Search)
            if selected_usecase in ["chatbot with web", "AI News"]:
                tavily_key = st.text_input(
                    "Enter Tavily API Key",
                    type="password",
                    placeholder="tavily_..."
                )
    
                self.user_controls["TAVILY_API_KEY"] = tavily_key
                st.session_state["TAVILY_API_KEY"] = tavily_key

                if tavily_key:
                    os.environ["TAVILY_API_KEY"] = tavily_key
                else:
                    st.warning("Please enter your Tavily API Key")
           
            # 5. Specialized Extra Options for News Node
            if selected_usecase == "AI News":
                st.subheader("AI News Explorer")
                time_frame = st.selectbox(
                    "Select Time Frame",
                    ["Daily", "Weekly", "Monthly"],
                    index=0
                )
                if st.button("Fetch Latest AI News", use_container_width=True):
                    st.session_state.IsFetchButtonClicked = True
                    st.session_state.TimeFrame = time_frame

        # Fixed syntax bug (Removed [DEFAULT])
        return {
            "usecase": selected_usecase,
            "user_controls": self.user_controls
        }