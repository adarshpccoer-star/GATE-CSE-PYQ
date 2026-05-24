import os
import json
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# Load environment variables from .env file securely
load_dotenv()

# Initialize ChromaDB - Changed to PersistentClient so your data actually saves to disk

# Initialize the OpenRouter client with optional (but recommended) headers
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:3000", # Can be any placeholder URL
        "X-OpenRouter-Title": "Agentic RAG Test App"
    }
)


def get_embedding(text):
    raw_response = client.embeddings.with_raw_response.create(
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",  # Highly reliable text embedding model
        input=text
    )
    response_json = json.loads(raw_response.content)
    
    # Let's add a robust fallback print statement to see errors if it happens again
    if "data" not in response_json:
        print(f"❌ OpenRouter Error: {response_json}")
        raise ValueError("No embedding data returned from provider.")
        
    return response_json["data"][0]["embedding"]

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection_langgraph = chroma_client.get_or_create_collection(name="langgraph_blogs")
collection_langchain = chroma_client.get_or_create_collection(name="langchain_blogs")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# --- DB 1: LangGraph Blogs ---
langgraph_blogs = [
    {"title": "LangGraph: Introduction and Launch Blog", "url": "https://www.langchain.com/blog/langgraph"},
    {"title": "LangChain and LangGraph Agent Frameworks Reach v1.0 Milestones", "url": "https://www.langchain.com/blog/langchain-langgraph-1dot0"},
    {"title": "LangGraph: Agent Orchestration Framework & Features", "url": "https://www.langchain.com/langgraph"}
]

for idx, item in enumerate(langgraph_blogs):
    print(f"Processing LangChain: {item['title']}...")
    try:
        loader = WebBaseLoader(item["url"])
        docs = loader.load()
        
        chunks = text_splitter.split_documents(docs)
        texts = [chunk.page_content for chunk in chunks]
        
        if not texts:
            continue
            
        embeddings = [get_embedding(text) for text in texts]
        metadatas = [{"source": item["title"], "url": item["url"]} for _ in texts]
        ids = [f"chain_doc_{idx}_chunk_{c_idx}" for c_idx in range(len(texts))]
        
        collection_langgraph.add(
            documents=texts, 
            embeddings=embeddings, 
            metadatas=metadatas, 
            ids=ids
        )
    except Exception as e:
        print(f"⚠️ Skipped {item['title']} due to network/scraping limitations: {e}")
# --- DB 2: LangChain Blogs ---
langchain_blogs = [
    {"title": "Official LangChain Blog Home", "url": "https://www.langchain.com/blog"},
    {"title": "LangChain Platform Overview: Observe, Evaluate, and Deploy", "url": "https://www.langchain.com/"},
    {"title": "LangChain and LangGraph 1.0 Design Philosophy", "url": "https://www.langchain.com/blog/langchain-langgraph-1dot0"},
    {"title": "LangChain Open Source Ecosystem & GitHub Repository", "url": "https://github.com/langchain-ai/langgraph"}
]

for idx, item in enumerate(langchain_blogs):
    print(f"Processing LangChain: {item['title']}...")
    try:
        loader = WebBaseLoader(item["url"])
        docs = loader.load()
        
        chunks = text_splitter.split_documents(docs)
        texts = [chunk.page_content for chunk in chunks]
        
        if not texts:
            continue
            
        embeddings = [get_embedding(text) for text in texts]
        metadatas = [{"source": item["title"], "url": item["url"]} for _ in texts]
        ids = [f"chain_doc_{idx}_chunk_{c_idx}" for c_idx in range(len(texts))]
        
        collection_langchain.add(
            documents=texts, 
            embeddings=embeddings, 
            metadatas=metadatas, 
            ids=ids
        )
    except Exception as e:
        print(f"⚠️ Skipped {item['title']} due to network/scraping limitations: {e}")
# --- DB 2: LangChain Blogs ---
print("\nBoth databases populated and saved successfully!")