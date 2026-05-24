import os
import json
import chromadb
from typing import Literal, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Import the core LangGraph components
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()

# --- Initialize Vector DB Collections ---
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_langgraph = chroma_client.get_or_create_collection(name="langgraph_blogs")
collection_langchain = chroma_client.get_or_create_collection(name="langchain_blogs")

# --- Initialize AI Clients ---
llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    system_instruction="You are a helpful assistant specialized in answering questions about LangChain and LangGraph."
)

# Native LangChain Gemini Embeddings
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")


# 1. Define the Shared Graph State
class AgentState(TypedDict):
    query: str
    collection_name: Literal["langgraph_blogs", "langchain_blogs"]
    result: str


# 2. Define the Graph Nodes (Python functions)

def router_node(state: AgentState) -> dict:
    """
    Node 1: Evaluates the incoming query and decides where to route it.
    Updates the 'collection_name' field in the state.
    """
    user_query = state["query"]
    
    system_prompt = (
        "You are a routing agent for a vector database. Examine the user's input query.\n"
        "If the query is primarily about agents, state machines, graphs, compilation, or LangGraph, reply with EXACTLY: langgraph_blogs\n"
        "If the query is about chains, expressions, basic prompts, or general LangChain features, reply with EXACTLY: langchain_blogs\n"
        "Do not include any other words, punctuation, or explanations."
    )
    
    response = llm_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User Query: {user_query}")
    ])
    
    chosen_collection = response.content.strip().replace('"', '').replace("'", "")
    print(f"🤖 [Router Node] Selected collection: {chosen_collection}")
    
    return {"collection_name": chosen_collection}


def retrieve_langgraph_node(state: AgentState) -> dict:
    """Node 2A: Handles retrieval and generation specifically for LangGraph knowledge."""
    print("📥 [Retrieval Node] Fetching from LangGraph Collections...")
    query_str = state["query"]
    
    # Using LangChain's Gemini embedding method natively
    embedded_query = gemini_embeddings.embed_query(query_str)
    db_response = collection_langgraph.query(query_embeddings=[embedded_query], n_results=3)
    
    retrieved_chunks = db_response.get("documents", [[]])[0]
    context_block = "\n---\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."
    
    generation_prompt = (
        f"Answer the user's question using ONLY the provided LangGraph context.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {query_str}"
    )
    llm_res = llm_model.invoke([HumanMessage(content=generation_prompt)])
    
    return {"result": llm_res.content}


def retrieve_langchain_node(state: AgentState) -> dict:
    """Node 2B: Handles retrieval and generation specifically for LangChain knowledge."""
    print("📥 [Retrieval Node] Fetching from LangChain Collections...")
    query_str = state["query"]
    
    # Using LangChain's Gemini embedding method natively
    embedded_query = gemini_embeddings.embed_query(query_str)
    db_response = collection_langchain.query(query_embeddings=[embedded_query], n_results=3)
    
    retrieved_chunks = db_response.get("documents", [[]])[0]
    context_block = "\n---\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."
    
    generation_prompt = (
        f"Answer the user's question using ONLY the provided LangChain context.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {query_str}"
    )
    llm_res = llm_model.invoke([HumanMessage(content=generation_prompt)])
    
    return {"result": llm_res.content}


# 3. Define the Routing Logic
def route_decision(state: AgentState) -> Literal["langgraph_blogs", "langchain_blogs"]:
    return state["collection_name"]


# 4. Build and Compile the Graph Workflow
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("langgraph_blogs", retrieve_langgraph_node)
workflow.add_node("langchain_blogs", retrieve_langchain_node)

workflow.add_edge(START, "router")

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "langgraph_blogs": "langgraph_blogs",
        "langchain_blogs": "langchain_blogs"
    }
)

workflow.add_edge("langgraph_blogs", END)
workflow.add_edge("langchain_blogs", END)

app = workflow.compile()


# 5. Invoke the Graph Workflow
chat = app.invoke({"query": "What is LangGraph?"})
print(chat)