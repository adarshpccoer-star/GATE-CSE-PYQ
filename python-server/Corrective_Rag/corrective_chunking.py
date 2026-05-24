import os
import json
import chromadb
from typing import Literal, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


text_embbedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview") # Native LangChain Gemini Embeddings
llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    system_instruction="You are a helpful assistant specialized in answering questions about LangChain and LangGraph."
) # Native LangChain Gemini LLM


chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_langgraph = chroma_client.get_or_create_collection(name="langgraph_blogs")
collection_langchain = chroma_client.get_or_create_collection(name="langchain_blogs")

class State(TypedDict):
    query: str

def retrival_from_vectorStore(state:State):
    embedded_query = text_embbedding.embed_query("query_string")




