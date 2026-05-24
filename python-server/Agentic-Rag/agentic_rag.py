import os
import uuid
import chromadb
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Clear the USER_AGENT warning log
os.environ["USER_AGENT"] = "CRAG Ingestion Bot/1.0"

load_dotenv()

# Initialize Embeddings
embeddings_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

def get_embeddings(texts):
    try:
        # Explicitly ensure we are passing clean, raw Python strings to the embedder
        clean_texts = [str(t) for t in texts]
        return embeddings_model.embed_documents(clean_texts)
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

# ChromaDB Setup
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_langgraph = chroma_client.get_or_create_collection(name="langgraph_blogs")
collection_langchain = chroma_client.get_or_create_collection(name="langchain_blogs")

# Keep a healthy chunk size so our CRAG evaluator has enough context later
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

langgraph_blogs = [
    {"title": "LangGraph Introduction", "url": "https://www.langchain.com/blog/langgraph"},
    {"title": "LangGraph v1 Release", "url": "https://www.langchain.com/blog/langchain-langgraph-1dot0"},
    {"title": "LangGraph Features", "url": "https://www.langchain.com/langgraph"}
]

langchain_blogs = [
    {"title": "LangChain Blog Home", "url": "https://www.langchain.com/blog"},
    {"title": "LangChain Platform Overview", "url": "https://www.langchain.com/"},
    {"title": "LangChain Design Philosophy", "url": "https://www.langchain.com/blog/langchain-langgraph-1dot0"},
    {"title": "LangChain GitHub", "url": "https://github.com/langchain-ai/langgraph"}
]

def ingest_blogs(blog_list, collection):
    for item in blog_list:
        print(f"\nProcessing: {item['title']}")
        try:
            # Check for duplication
            existing = collection.get(where={"url": item["url"]})
            if existing["ids"]:
                print("Already exists → skipping")
                continue

            loader = WebBaseLoader(web_paths=(item["url"],))
            docs = loader.load()
            
            # Split documents
            chunks = text_splitter.split_documents(docs)
            
            # Clean up the texts and isolate them into a clean string list
            texts = [str(chunk.page_content).strip() for chunk in chunks if chunk.page_content.strip()]

            if not texts:
                print("No text extracted")
                continue

            vector_embeddings = get_embeddings(texts)
            if vector_embeddings is None:
                print("Skipped due to empty embeddings vector calculation")
                continue

            print(f"  -> Match Verify: Docs Count ({len(texts)}) vs Vectors Count ({len(vector_embeddings)})")

            # Double check to prevent ChromaDB crash if an embedding mismatch still slips by
            if len(texts) != len(vector_embeddings):
                print(f"⚠️ Mismatch detected! Remapping embeddings element-by-element...")
                vector_embeddings = [embeddings_model.embed_query(t) for t in texts]

            metadatas = [{"source": item["title"], "url": item["url"]} for _ in texts]
            ids = [str(uuid.uuid4()) for _ in texts]

            collection.add(
                documents=texts,
                embeddings=vector_embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Stored {len(texts)} chunks successfully")

        except Exception as e:
            print(f"❌ Skipped {item['title']}. Reason: {e}")

if __name__ == "__main__":
    print("\n=== Loading LangGraph Blogs ===")
    ingest_blogs(langgraph_blogs, collection_langgraph)

    print("\n=== Loading LangChain Blogs ===")
    ingest_blogs(langchain_blogs, collection_langchain)
    print("\nData ingestion completed.")