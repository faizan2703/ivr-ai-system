"""Knowledge base management routes"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from datetime import datetime
from app.models.schemas import (
    DocumentRequest, DocumentResponse, DocumentListResponse,
    SearchRequest, SearchResponse, SearchResult
)

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge-base"])

# Service instance
rag_service = None


@router.post("/documents", response_model=DocumentResponse)
async def add_document(request: DocumentRequest):
    """Add document to knowledge base"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        result = rag_service.add_document(
            title=request.title,
            content=request.content,
            category=request.category,
            tags=request.tags
        )
        return DocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all documents in knowledge base"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        result = rag_service.get_all_documents()
        return DocumentListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    """Search knowledge base"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        docs = rag_service.search_documents(
            query=request.query,
            top_k=request.top_k
        )
        
        results = [
            SearchResult(**doc)
            for doc in docs
        ]
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document file"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        contents = await file.read()
        text_content = contents.decode("utf-8")
        
        # Add to knowledge base
        result = rag_service.add_document(
            title=file.filename or "Uploaded Document",
            content=text_content,
            category="uploaded"
        )
        
        return {
            "message": "Document uploaded successfully",
            "document_id": result["document_id"],
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document from knowledge base"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    
    try:
        success = rag_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
