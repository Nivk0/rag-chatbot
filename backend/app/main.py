from pathlib import Path
import json
import shutil
import mimetypes
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uuid
from .models.document import Document, Query, ChatResponse
from .services.document_processor import DocumentProcessor
from .services.vector_store import VectorStore
from .services.embeddings import EmbeddingService
from .services.openai_service import OpenAIService
from .core.config import settings

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
DOCUMENTS_FILE = Path("documents.json")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize services
doc_processor = DocumentProcessor()
vector_store = VectorStore()
embedding_service = EmbeddingService(settings.EMBEDDINGS_MODEL)
openai_service = OpenAIService()

def load_documents():
    if DOCUMENTS_FILE.exists():
        return json.loads(DOCUMENTS_FILE.read_text())
    return []

def save_documents(documents):
    DOCUMENTS_FILE.write_text(json.dumps(documents))

@app.get("/")
async def root():
    return {
        "message": "Welcome to the RAG Chatbot API",
        "endpoints": {
            "GET /documents": "List all documents",
            "POST /documents/upload": "Upload new documents",
            "DELETE /documents/{document_id}": "Delete a specific document",
            "POST /chat": "Chat with the documents",
            "/uploads/*": "Static file access"
        }
    }

@app.get("/documents")
async def get_documents():
    try:
        return load_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload")
async def upload_documents(files: List[UploadFile]):
    try:
        existing_documents = load_documents()
        new_documents = []
        
        for file in files:
            doc_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
            
            with file_path.open("wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            doc = {
                "id": doc_id,
                "name": file.filename,
                "file_path": f"/uploads/{file_path.name}",
                "content_type": mimetypes.guess_type(file.filename)[0],
                "size": len(content)
            }
            new_documents.append(doc)
            
            # Process document for vector store
            result = doc_processor.process_document(content, file.filename, doc["content_type"])
            
            # Log the chunks
            for i, chunk in enumerate(result["chunks"]): print(f"Chunk {i} of document {file.filename}: {chunk}\n")
            
            metadata = [{
                "chunk_index": i,
                "filename": file.filename,
                "file_path": doc["file_path"],
                "content": chunk
            } for i, chunk in enumerate(result["chunks"])]
            
            # Store embeddings for this specific document
            vector_store.add_document(doc_id, result["embeddings"], metadata)
        
        all_documents = existing_documents + new_documents
        save_documents(all_documents)
        return new_documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    try:
        documents = load_documents()
        document = next((doc for doc in documents if doc["id"] == document_id), None)
        
        if document:
            # Remove from documents list
            documents = [doc for doc in documents if doc["id"] != document_id]
            save_documents(documents)
            
            # Delete from vector store
            vector_store.delete_document(document_id)
            
            # Delete file
            file_path = UPLOAD_DIR / Path(document["file_path"]).name
            if file_path.exists():
                file_path.unlink()
                
            return {"message": "Document deleted successfully"}
        raise HTTPException(status_code=404, detail="Document not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(query: Query):
    try:
        if not query.document_ids:
            raise HTTPException(status_code=400, detail="No documents specified for chat")
        
        query_embedding = embedding_service.get_embeddings([query.text])[0]
        
        results = vector_store.search(
            query_vector=query_embedding,
            document_ids=query.document_ids
        )
                
        context = [
            f"Content: {result.payload['content']}\n"
            f"Source: {result.payload['filename']}"
            for result in results
        ]
        
        response = await openai_service.generate_response(query.text, context)
        return ChatResponse(response=response)
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
