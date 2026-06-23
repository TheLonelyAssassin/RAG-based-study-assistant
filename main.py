from fastapi import FastAPI, UploadFile, File,HTTPException
from pydantic import BaseModel
from typing import List
import RaG,tempfile
app =FastAPI()

class QueryRequest(BaseModel):
    question:str

all_chunks=[]
all_embeddings=[]

@app.get("/")
def read_root():
    return {"status":"Alive"}

@app.post("/query")
def query(request: QueryRequest):
    if not all_chunks:
        raise HTTPException(status_code=400, detail="No documents indexed yet. Upload a document first.")
    quest = request.question
    answer, contex = RaG.retri_generate(quest, all_chunks, all_embeddings)
    return {"answer": answer}
@app.post("/upload")
async def read_file(files: List[UploadFile] = File(...)):
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False,
                                            suffix="."+file.filename.split(".")[-1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
            if file.filename.endswith(".pdf"):
                document = RaG.read_pdf(tmp_path)
            elif file.filename.endswith(".docx"):
                document = RaG.read_docx(tmp_path)
            else: raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")
            chunk, embeding = RaG.emd_chunk(document, max_sent=10, overlap=2)
            all_chunks.extend(chunk)
            all_embeddings.extend(embeding)
    return {"status": "indexed", "chunks": len(all_chunks)}
@app.delete("/documents")
def clear_doc():
    all_chunks.clear()
    all_embeddings.clear()
    return {"status": "cleared"}