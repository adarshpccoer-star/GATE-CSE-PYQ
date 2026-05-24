import os
import chromadb
from typing import List, Dict, Any
from typing_extensions import TypedDict
from dotenv import load_dotenv

# Use operator to define how LangGraph handles merging state values
import operator

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from tavily import TavilyClient

load_dotenv()

# Initialize Models
llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# Vector DB & Search Client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_langgraph = chroma_client.get_or_create_collection(name="langgraph_blogs")
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 1. Define Graph State with a Reducer Function
class State(TypedDict):
    question: str
    documents: List[str]  # We manage manual state reassignment safely in the nodes
    steps: List[str]
    web_search: str  # "Yes" or "No"
    generation: str

# 2. Pydantic Grading Schema
class GradeDocuments(BaseModel):
    binary_scores: List[str] = Field(
        description="A list of 'yes' or 'no' scores matching the order of the provided documents."
    )

def get_embedding(text: str) -> List[float]:
    """Helper method to convert raw query text into vector embedding."""
    return embeddings.embed_query(text)

# 3. Define Pipeline Nodes
def retrieval_from_vector_store(state: State) -> Dict[str, Any]:
    print("\n=== 🔍 RETRIEVING FROM VECTOR STORE ===")
    embedded_query = get_embedding(state["question"])

    response = collection_langgraph.query(
        query_embeddings=[embedded_query],
        n_results=3
    )

    docs = response["documents"][0] if response["documents"] else []
    distances = response["distances"][0] if response["distances"] else []

    print("Retrieved Document Metrics:")
    for i, (d, dist) in enumerate(zip(docs, distances)):
        print(f"  Chunk {i+1} -> Vector Distance Score: {dist:.4f}")

    return {
        "documents": docs,
        "steps": ["retrieval_from_vector_store"],
        "web_search": "No"
    }

def grader_docs(state: State) -> Dict[str, Any]:
    print("\n=== 📝 GRADING RETRIEVED DOCUMENTS ===")
    structured_llm_grader = llm_model.with_structured_output(GradeDocuments)
    
    system_prompt = """You are an expert grader assessing the relevance of a list of retrieved documents to a user question.
Analyze each document independently. For each document, if it contains keywords or semantic meaning related to the user question, grade it as 'yes'. Otherwise, grade it as 'no'.
Return your answers as a list matching the exact order of the documents."""
    
    grader_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "User Question: {question}\n\nRetrieved Document Chunks:\n{document}")
    ])
    
    doc_grader = grader_prompt | structured_llm_grader
    filter_docs = []
    web_search_flag = "No"

    # Handle empty states safely
    if not state["documents"]:
        print("⚠️ No documents retrieved to grade! Defaulting straight to Web Search.")
        return {"documents": [], "web_search": "Yes", "steps": ["grader_docs"]}

    for doc in state["documents"]:
        score = doc_grader.invoke({
            "question": state["question"],
            "document": doc
        })
        if score.binary_score.lower() == "yes":
            print("  ✅ Chunk Status -> RELEVANT")
            filter_docs.append(doc)
        else:
            print("  ❌ Chunk Status -> NOT RELEVANT")

    # If NO documents pass the grading test, trigger search
    if not filter_docs:
        print("⚠️ All local documentation failed relevance test. Fallback Web Search activated.")
        web_search_flag = "Yes"

    return {
        "documents": filter_docs, 
        "steps": ["grader_docs"],
        "web_search": web_search_flag
    }

def web_search(state: State) -> Dict[str, Any]:
    print("\n=== 🌐 EXECUTING WEB SEARCH FALLBACK ===")
    search_results = tavily_client.search(query=state["question"])
    
    # Isolate web contents safely
    results_list = [r.get("content", "") for r in search_results.get("results", []) if r.get("content")]
    
    # CRITICAL FIX: Retain previously graded valid local docs, and extend them with web findings!
    current_docs = list(state.get("documents", []))
    current_docs.extend(results_list)

    print(f"  Merged {len(results_list)} live web snippets with your pipeline context.")

    return {
        "documents": current_docs,
        "steps": ["web_search"]
    }

def generate_summary(state: State) -> Dict[str, Any]:
    print("\n=== 🧠 GENERATING FINAL RESPONSE ===")
    documents = state["documents"]
    
    if not documents:
        context_str = "No verified source material found across local database search or live web indices."
    else:
        context_str = "\n\n---\n\n".join(documents)

    prompt = ChatPromptTemplate.from_template(
        """You are an advanced technical assistant answering questions based on verified blog logs and web reports.
Generate a comprehensive, structural response for the user question using exclusively the context blocks provided below.

Question:
{question}

Context Materials:
{context}
"""
    )

    chain = prompt | llm_model
    llm_res = chain.invoke({
        "question": state["question"],
        "context": context_str
    })
    
    return {
        "generation": llm_res.content,
        "steps": ["generate_summary"]
    }

# 4. Conditional Edge Routing Logic
def decide_to_generate(state: State) -> str:
    if state["web_search"] == "Yes":
        return "web_search"
    return "generate_summary"

# 5. Build and Compile LangGraph Workflow
workflow = StateGraph(State)

workflow.add_node("retrieval_from_vector_store", retrieval_from_vector_store)
workflow.add_node("grader_docs", grader_docs)
workflow.add_node("web_search", web_search)
workflow.add_node("generate_summary", generate_summary)

workflow.add_edge(START, "retrieval_from_vector_store")
workflow.add_edge("retrieval_from_vector_store", "grader_docs")

workflow.add_conditional_edges(
    "grader_docs",
    decide_to_generate,
    {
        "web_search": "web_search",
        "generate_summary": "generate_summary"
    }
)

workflow.add_edge("web_search", "generate_summary")
workflow.add_edge("generate_summary", END)

app = workflow.compile()

# 6. Run Application Execution Check
if __name__ == "__main__":
    inputs = {"question": "What is LangGraph and how does it use state?"}
    output = app.invoke(inputs)
    print("\n================ FINAL GENERATION RESULT ================")
    print(output["generation"])
    print("=========================================================")