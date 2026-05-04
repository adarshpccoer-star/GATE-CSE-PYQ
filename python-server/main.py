import os
import shutil
from processors.text_parser import extract_clean_pages
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/process-pdfs")
async def process_pdfs(questions: UploadFile = File(...)):
   
    if not questions.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

   
    temp_path = f"temp_{questions.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(questions.file, buffer)

    try:
       
        raw_pages = extract_clean_pages(temp_path)
        
        return {
            "filename": questions.filename,
            "page_count": len(raw_pages),
            "data": raw_pages
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 5. Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)