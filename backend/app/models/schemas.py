"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CallState(str, Enum):
    """Call states"""
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    ACTIVE = "active"
    ENDED = "ended"
    FAILED = "failed"


class MessageType(str, Enum):
    """Message types in conversation"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


# === Call Management ===
class CallRequest(BaseModel):
    """Request to initiate a call"""
    user_name: str = Field(..., min_length=1, max_length=100)
    user_phone: str = Field(..., pattern=r"^\+?1?\d{9,15}$")
    call_topic: str = Field(..., min_length=1, max_length=200)
    language: str = "en"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_name": "John Doe",
                "user_phone": "+1234567890",
                "call_topic": "billing inquiry",
                "language": "en"
            }
        }


class CallResponse(BaseModel):
    """Response with call details"""
    call_id: str
    status: CallState
    message: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "call_id": "call_123456",
                "status": "initiated",
                "message": "Call initiated successfully",
                "timestamp": "2024-02-09T10:00:00"
            }
        }


class CallStatusResponse(BaseModel):
    """Call status response"""
    call_id: str
    status: CallState
    duration: int  # seconds
    message_count: int
    created_at: datetime
    updated_at: datetime


# === Conversation ===
class ConversationMessage(BaseModel):
    """A message in conversation"""
    id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationRequest(BaseModel):
    """Request for message in ongoing call"""
    call_id: str
    message: str = Field(..., min_length=1, max_length=1000)


class ConversationResponse(BaseModel):
    """Response to user message"""
    call_id: str
    agent_response: str
    intent: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_transfer: bool = False
    transfer_reason: Optional[str] = None
    timestamp: datetime


class ConversationHistoryResponse(BaseModel):
    """Full conversation history"""
    call_id: str
    messages: List[ConversationMessage]
    summary: str
    call_status: CallState


# === Knowledge Base ===
class DocumentRequest(BaseModel):
    """Request to add document to knowledge base"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    category: str = Field(default="general")
    tags: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Billing FAQ",
                "content": "How to check your bill...",
                "category": "billing",
                "tags": ["billing", "faq"]
            }
        }


class DocumentResponse(BaseModel):
    """Response for document operations"""
    document_id: str
    title: str
    category: str
    created_at: datetime
    message: str


class DocumentListResponse(BaseModel):
    """List of documents in knowledge base"""
    documents: List[Dict[str, Any]]
    total: int
    categories: List[str]


class SearchRequest(BaseModel):
    """Request to search knowledge base"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class SearchResult(BaseModel):
    """Search result from knowledge base"""
    document_id: str
    title: str
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    category: str


class SearchResponse(BaseModel):
    """Response with search results"""
    query: str
    results: List[SearchResult]
    total_results: int


# === System Health ===
class HealthResponse(BaseModel):
    """System health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]  # {service_name: status}


# === Error Response ===
class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
