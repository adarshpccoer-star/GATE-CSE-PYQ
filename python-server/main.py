## main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import uvicorn

from processors.text_parser import extract_text_from_pdf
from processors.table_parser import extract_tables_from_pdf
from processors.openai import change_parse_text_to_JSON

# Switched to the more basic splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Backend Running"}

@app.post("/process-pdfs")
async def process_pdfs(
    questions: UploadFile = File(...),
    answers: UploadFile = File(...)
):
    try:
        # 1. Read files
        q_content = await questions.read()
        a_content = await answers.read()

        # 2. Extract content
        q_text = extract_text_from_pdf(q_content)
        a_tables = extract_tables_from_pdf(a_content)

        # 3. Simple Character Splitting (No tiktoken required)
        # We use RecursiveCharacterTextSplitter but without the tiktoken encoder.
        # This splits by characters: "\n\n", "\n", " ", and "" in order.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,     # ~1000 tokens roughly
            chunk_overlap=200,   # small overlap to preserve context
            length_function=len, # use standard Python len()
        )
        
        chunks = text_splitter.split_text(q_text)
        
        # We'll take the first chunk to send to OpenAI
        # This avoids the "tiktoken" dependency entirely
        final_input_text = chunks[0] if chunks else q_text[:4000]

        # 4. Process with OpenAI
        data = await change_parse_text_to_JSON(final_input_text)

        return {
            "success": True,
            "questionJSON": jsonable_encoder(data),
            "answers_tables": a_tables
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "success": False,
            "type": type(e).__name__,
            "details": str(e),
            "message": "Processing failed."
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)