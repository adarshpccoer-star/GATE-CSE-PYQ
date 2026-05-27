import streamlit as st
from src.langgraph.ui.uiconfigfile import Config
import os

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):

        st.set_page_config(
            page_title="LangGraph",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.header(f"🤖 {self.config.get_page_title()}")

        with st.sidebar:

            st.title("Settings")

            # LLM Selection
            llm_options = self.config.get_llm_options()

            self.user_controls["select_llm"] = st.selectbox(
                "Select LLM Provider",
                llm_options
            )

            # GROQ Section
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

            # Use Case Selection
            usecase_options = self.config.get_usecase_options()

            self.user_controls["select_usecase"] = st.selectbox(
                "Select Use Case",
                usecase_options
            )

            if self.user_controls["select_usecase"] == "chatbot with web":
                tavily_key = st.text_input(
                  "Enter Tavily API Key",
                  type="password",
                 placeholder="tavily_..."
                 )
    
                self.user_controls["TAVILY_API_KEY"] = tavily_key
                st.session_state["TAVILY_API_KEY"] = tavily_key

            # Dynamically inject into environment variables for TavilySearchAPIWrapper to find
                if tavily_key:
                 os.environ["TAVILY_API_KEY"] = tavily_key
                else:
                 st.warning("Please enter your Tavily API Key")

        return self.user_controls