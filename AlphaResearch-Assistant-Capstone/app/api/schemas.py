"""API Models and Schemas"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============ Request Models ============

class AskRequest(BaseModel):
    """Query request model"""
    question: str = Field(..., min_length=1, max_length=5000, description="User question")
    session_id: str = Field(default="default", description="Conversation session id")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Recent chat turns")
    enable_reasoning: bool = Field(default=True, description="Enable multi-agent reasoning")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    style: str = Field(default="professional", description="Response style")
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()


class DocumentUploadRequest(BaseModel):
    """Document metadata for upload"""
    filename: str = Field(..., description="Document filename")
    document_type: Optional[str] = Field(default="general", description="Document type")
    source: Optional[str] = Field(default="user_upload", description="Document source")
    tags: List[str] = Field(default_factory=list, description="Document tags")


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Similarity threshold")


class BatchIngestRequest(BaseModel):
    """Batch document ingestion request"""
    directory_path: str = Field(..., description="Directory containing documents")
    recursive: bool = Field(default=True, description="Process recursively")
    file_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".md"],
        description="File extensions to process"
    )


# ============ Response Models ============

class DocumentMetadata(BaseModel):
    """Document metadata"""
    source: str
    section: Optional[str] = None
    chunk_id: int
    upload_date: datetime
    page_number: Optional[int] = None


class RetrievalResult(BaseModel):
    """Single retrieval result"""
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    source_file: str


class AskResponse(BaseModel):
    """Response to user question"""
    question: str
    answer: str
    sources: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    retrieval_summary: Dict[str, Any] = {}
    execution_time_ms: float
    status: str = "success"
    error: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[RetrievalResult]
    total_found: int
    execution_time_ms: float


class HealthStatus(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime
    services: Dict[str, str] = {
        "vector_db": "operational",
        "llm_service": "operational",
        "retrieval_service": "operational"
    }


class DocumentIngestResponse(BaseModel):
    """Document ingestion response"""
    status: str
    ingested_documents: int
    failed_documents: int
    total_chunks: int
    execution_time_ms: float
    details: List[Dict[str, Any]] = []


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PlanResponse(BaseModel):
    """Agent planning response"""
    query_type: str
    subtasks: List[str]
    key_concepts: List[str]
    expected_length: str
    complexity: str


class ReasoningResponse(BaseModel):
    """Reasoning agent response"""
    key_insights: List[str]
    contradictions: List[str]
    confidence: float
    gaps: List[str]
    summary: str


class MultiAgentResponse(BaseModel):
    """Full multi-agent response"""
    question: str
    answer: str
    confidence: float
    plan: PlanResponse
    retrieval_summary: List[Dict[str, Any]]
    reasoning: Optional[ReasoningResponse] = None
    status: str
    execution_time_ms: float = 0.0
