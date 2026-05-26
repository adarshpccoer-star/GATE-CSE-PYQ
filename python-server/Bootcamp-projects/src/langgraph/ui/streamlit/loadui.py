import streamlit as st
from src.langgraph.ui.uiconfigfile import Config


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

        return self.user_controls