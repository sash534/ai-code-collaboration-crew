from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Google Drive Mock Service", version="1.0.0")

documents: dict[str, dict] = {}
doc_counter = 0


class CreateDocumentRequest(BaseModel):
    title: str
    content: str = ""


class UpdateDocumentRequest(BaseModel):
    content: str
    mode: str = "append"


@app.post("/api/documents")
async def create_document(req: CreateDocumentRequest):
    global doc_counter
    doc_counter += 1
    doc_id = f"doc-{doc_counter:04d}"
    doc = {
        "id": doc_id,
        "title": req.title,
        "content": req.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }
    documents[doc_id] = doc
    return doc


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    return documents[doc_id]


@app.put("/api/documents/{doc_id}")
async def update_document(doc_id: str, req: UpdateDocumentRequest):
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    doc = documents[doc_id]
    if req.mode == "append":
        doc["content"] += "\n" + req.content
    else:
        doc["content"] = req.content
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    return doc


@app.get("/api/documents")
async def list_documents():
    return {"results": list(documents.values()), "total": len(documents)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "documents_count": len(documents)}
