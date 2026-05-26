import os
import streamlit as st
from langchain_groq import ChatGroq


class GroqLLM:

    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):

        try:
            groq_api_key = self.user_controls_input.get(
                "GROQ_API_KEY",
                os.getenv("GROQ_API_KEY", "")
            )

            selected_groq_model = self.user_controls_input.get(
                "select_groq_model"
            )

            if not groq_api_key:
                st.error(
                    "Groq API Key is missing. "
                    "Please enter it in the sidebar."
                )
                st.stop()

            llm = ChatGroq(
                api_key=groq_api_key,
                model=selected_groq_model
            )

            return llm

        except Exception as e:
            raise ValueError(f"Error loading Groq LLM: {e}")