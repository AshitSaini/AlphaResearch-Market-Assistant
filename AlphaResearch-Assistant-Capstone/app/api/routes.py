"""FastAPI Routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, BackgroundTasks
from typing import List, Optional
import logging
import time
import re
from datetime import datetime

from app.api.schemas import (
    AskRequest, AskResponse, SearchRequest, SearchResponse,
    HealthStatus, DocumentUploadRequest, ErrorResponse,
    DocumentIngestResponse, BatchIngestRequest
)
from app.core.rag_pipeline import RAGPipeline
from app.agents.orchestrator import MultiAgentOrchestrator
from app.services.document_service import DocumentService
from app.services.official_source_service import OfficialSourceService
from app.services.llm_service import LLMService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
rag_pipeline = RAGPipeline()
orchestrator = MultiAgentOrchestrator()
doc_service = DocumentService()
official_sources = OfficialSourceService()
llm_service = LLMService()
conversation_memory: dict[str, List[dict]] = {}
last_substantial_answer_by_session: dict[str, str] = {}
last_substantial_answer_global: str = ""


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        version=settings.PROJECT_VERSION,
        timestamp=datetime.now(),
        services={
            "vector_db": "operational",
            "llm_service": "operational",
            "retrieval_service": "operational"
        }
    )


@router.post("/ask", response_model=AskResponse, responses={400: {"model": ErrorResponse}})
async def ask_question(request: AskRequest):
    """
    Ask a question using multi-agent RAG system
    
    - **question**: User query
    - **enable_reasoning**: Use multi-agent reasoning
    - **top_k**: Number of documents to retrieve
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing question: {request.question[:100]}")
        session_id = request.session_id or "default"
        server_history = conversation_memory.get(session_id, [])
        effective_history = request.conversation_history or server_history
        
        follow_up_answer = _answer_direct_follow_up(
            request.question,
            effective_history
        )

        if follow_up_answer:
            _remember_turns(session_id, request.question, follow_up_answer)
            execution_time = (time.time() - start_time) * 1000
            return AskResponse(
                question=request.question,
                answer=follow_up_answer,
                sources=[],
                confidence=0.9,
                retrieval_summary={
                    "mode": "conversation_follow_up",
                    "subtasks_processed": 0,
                    "documents_retrieved": 0
                },
                execution_time_ms=execution_time,
                status="success"
            )
        if _is_follow_up_request(request.question) and not effective_history:
            fallback_answer = _get_last_substantial_answer(session_id)
            if fallback_answer:
                follow_up_answer = _answer_direct_follow_up(
                    request.question,
                    [{"role": "assistant", "content": fallback_answer}]
                )
                if follow_up_answer:
                    _remember_turns(session_id, request.question, follow_up_answer)
                    execution_time = (time.time() - start_time) * 1000
                    return AskResponse(
                        question=request.question,
                        answer=follow_up_answer,
                        sources=[],
                        confidence=0.9,
                        retrieval_summary={
                            "mode": "conversation_follow_up_global_fallback",
                            "subtasks_processed": 0,
                            "documents_retrieved": 0
                        },
                        execution_time_ms=execution_time,
                        status="success"
                    )
            execution_time = (time.time() - start_time) * 1000
            return AskResponse(
                question=request.question,
                answer=(
                    "I need the previous answer to summarize it. Please ask the original question again, "
                    "or avoid clearing/refreshing the chat before asking a follow-up."
                ),
                sources=[],
                confidence=0.0,
                retrieval_summary={
                    "mode": "missing_conversation_context",
                    "subtasks_processed": 0,
                    "documents_retrieved": 0
                },
                execution_time_ms=execution_time,
                status="success"
            )

        contextual_question = _build_contextual_question(
            request.question,
            effective_history
        )

        if request.enable_reasoning:
            result = orchestrator.execute(
                query=contextual_question,
                enable_reasoning=True,
                top_k=request.top_k
            )
        else:
            result = rag_pipeline.execute(
                question=contextual_question,
                top_k=request.top_k,
                include_reasoning=False
            )
        
        if result.get("status") == "failed":
            raise HTTPException(
                status_code=500,
                detail="Failed to process question"
            )
        
        execution_time = (time.time() - start_time) * 1000
        answer_text = result.get("answer", "") or ""
        _remember_turns(session_id, request.question, answer_text)
        
        return AskResponse(
            question=request.question,
            answer=answer_text,
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            retrieval_summary={
                "mode": "multi_agent" if request.enable_reasoning else "fast_rag",
                "subtasks_processed": len(result.get("retrieval_summary", [])),
                "documents_retrieved": result.get("num_documents_retrieved", 0) or sum(
                    r.get("document_count", 0)
                    for r in result.get("retrieval_summary", [])
                )
            },
            execution_time_ms=execution_time,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        execution_time = (time.time() - start_time) * 1000
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search knowledge base
    
    - **query**: Search query
    - **top_k**: Number of results
    - **threshold**: Minimum similarity score (0-1)
    """
    start_time = time.time()
    
    try:
        logger.info(f"Searching: {request.query}")
        
        results = rag_pipeline.retrieval_service.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        # Format results
        formatted_results = []
        documents = results.get('documents', [[]])[0] or []
        metadatas = results.get('metadatas', [[]])[0] or []
        similarities = results.get('similarities', [])
        
        for i, (doc, meta, similarity) in enumerate(zip(documents, metadatas, similarities)):
            formatted_results.append({
                "content": doc,
                "similarity_score": similarity,
                "metadata": meta,
                "source_file": meta.get('source', 'unknown')
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_found=len(formatted_results),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )


def _build_contextual_question(question: str, history: List[dict]) -> str:
    """Attach recent turns so short follow-ups are answered in context."""
    if not history:
        return question

    recent = history[-6:]
    formatted_turns = []
    for turn in recent:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        formatted_turns.append(f"{role.title()}: {content[:1200]}")

    if not formatted_turns:
        return question

    return (
        "Use the recent conversation to interpret the user's latest request. "
        "If the latest request asks to simplify, summarize, compare, continue, or clarify, "
        "apply it to the immediately preceding assistant answer.\n\n"
        "Recent conversation:\n"
        + "\n\n".join(formatted_turns)
        + f"\n\nLatest user request: {question}"
    )


def _answer_direct_follow_up(question: str, history: List[dict]) -> Optional[str]:
    """Answer rewrite/simplification follow-ups directly from the previous answer."""
    normalized = question.lower().strip()
    if not _is_follow_up_request(normalized):
        return None
    if not history:
        return None

    previous_answer = ""
    for turn in reversed(history):
        if turn.get("role") == "assistant" and _is_substantial_answer(turn.get("content", "")):
            previous_answer = turn["content"]
            break

    if not previous_answer:
        previous_answer = _get_last_substantial_answer("default")

    if not previous_answer:
        return None

    requested_lines = _requested_line_count(question)
    requested_words = _requested_word_count(question)

    if requested_lines:
        return _force_numbered_lines(previous_answer, requested_lines)

    line_instruction = (
        f"Return exactly {requested_lines} numbered lines. Each line must be one complete, useful point. "
        "Do not return a title or introduction.\n"
        if requested_lines
        else ""
    )
    word_instruction = (
        f"Return approximately {requested_words} words. Stay within plus or minus 10 words. "
        "Do not return a title unless needed.\n"
        if requested_words and not requested_lines
        else ""
    )

    prompt = (
        "You are AlphaResearch Assistant. The user is asking a follow-up about your previous answer. "
        "Do not retrieve new facts. Rewrite the previous answer according to the latest request. "
        f"{line_instruction}{word_instruction}"
        "Keep it clear, professional, and concise.\n\n"
        f"Previous answer:\n{previous_answer[:5000]}\n\n"
        f"Latest request:\n{question}"
    )
    answer = llm_service.generate_quick_response(prompt, max_tokens=900)

    if requested_lines and _count_numbered_lines(answer) < requested_lines:
        retry_prompt = (
            f"Rewrite the previous answer into EXACTLY {requested_lines} numbered lines. "
            "No heading. No paragraph. No extra text before or after. "
            "Each line must begin with '1.' through the final number.\n\n"
            f"Previous answer:\n{previous_answer[:5000]}"
        )
        answer = llm_service.generate_quick_response(retry_prompt, max_tokens=900)

    if requested_lines and _count_numbered_lines(answer) < requested_lines:
        answer = _force_numbered_lines(previous_answer, requested_lines)

    return answer


def _remember_turns(session_id: str, user_question: str, assistant_answer: str) -> None:
    """Store recent server-side turns as a fallback for follow-up questions."""
    global last_substantial_answer_global

    turns = conversation_memory.setdefault(session_id, [])
    turns.append({"role": "user", "content": user_question})
    turns.append({"role": "assistant", "content": assistant_answer})
    conversation_memory[session_id] = turns[-12:]

    if _is_substantial_answer(assistant_answer):
        last_substantial_answer_by_session[session_id] = assistant_answer
        last_substantial_answer_global = assistant_answer


def _get_last_substantial_answer(session_id: str) -> str:
    return last_substantial_answer_by_session.get(session_id) or last_substantial_answer_global


def _is_substantial_answer(answer: str) -> bool:
    text = (answer or "").strip()
    if len(text) < 120:
        return False
    if len(text.splitlines()) <= 2 and len(text.split()) < 30:
        return False
    return True


def _is_follow_up_request(question: str) -> bool:
    normalized = question.lower().strip()
    followup_terms = [
        "simplify",
        "summarize",
        "summarise",
        "summary",
        "line",
        "lines",
        "word",
        "words",
        "short",
        "brief",
        "explain simply",
        "make it simple",
        "easy understanding",
        "continue",
        "above",
        "previous",
    ]
    return any(term in normalized for term in followup_terms)


def _requested_line_count(question: str) -> Optional[int]:
    normalized = question.lower().replace("-", " ")
    match = re.search(r"\b(?:in|into|as|within)\s+(\d{1,2})\s+lines?\b", normalized)
    if not match:
        match = re.search(r"\b(\d{1,2})\s+lines?\b", normalized)
    if not match:
        return None
    return max(1, min(int(match.group(1)), 20))


def _requested_word_count(question: str) -> Optional[int]:
    normalized = question.lower().replace("-", " ")
    match = re.search(r"\b(?:in|into|as|within)\s+(\d{1,3})\s+words?\b", normalized)
    if not match:
        match = re.search(r"\b(\d{1,3})\s+words?\b", normalized)
    if not match:
        return None
    return max(20, min(int(match.group(1)), 500))


def _count_numbered_lines(text: str) -> int:
    return len(re.findall(r"(?m)^\s*\d+\.\s+\S+", text or ""))


def _force_numbered_lines(previous_answer: str, count: int) -> str:
    """Deterministically create numbered points if the model ignores line count."""
    text = re.sub(r"(?m)^#+\s*", "", previous_answer or "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = "\n".join(
        line
        for line in text.splitlines()
        if "|" not in line and not re.match(r"^\s*-{3,}\s*$", line)
    )

    list_items = []
    for line in text.splitlines():
        has_list_marker = bool(re.match(r"^\s*(?:[-*]|\d+[.)])\s+", line))
        clean_line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", line).strip()
        clean_line = clean_line.strip(" -:\t")
        if (
            has_list_marker
            and
            len(clean_line) > 24
            and not clean_line.lower().startswith(("top ", "summary", "conclusion", "overview", "below "))
        ):
            list_items.append(clean_line)

    if len(list_items) >= count:
        return "\n".join(f"{index}. {point[:220].rstrip('.')}" for index, point in enumerate(list_items[:count], start=1))

    text = re.sub(r"(?m)^\s*[-*]\s+", "", text)
    text = re.sub(r"(?m)^\s*\d+\.\s+", "", text)
    candidates = [
        item.strip(" -:\n\t")
        for item in re.split(r"(?<=[.!?])\s+|\n+", text)
        if len(item.strip()) > 35
        and not item.strip().lower().startswith(("below is", "key differences", "comparison basis", "top "))
    ]

    seen = set()
    unique = []
    for item in candidates:
        key = item.lower()[:90]
        if key not in seen:
            unique.append(item)
            seen.add(key)

    if not unique:
        unique = ["The previous answer should be read in the context of the earlier question."]

    while len(unique) < count:
        unique.append(unique[-1])

    return "\n".join(f"{index}. {point[:220].rstrip('.')}" for index, point in enumerate(unique[:count], start=1))


@router.get("/search", response_model=SearchResponse)
async def search_documents_get(
    query: str = Query(..., min_length=1, max_length=1000),
    limit: int = Query(5, ge=1, le=20),
    threshold: float = Query(0.0, ge=0.0, le=1.0),
):
    """Search knowledge base with query parameters."""
    return await search_documents(SearchRequest(query=query, top_k=limit, threshold=threshold))


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest document
    
    Supports: PDF, DOCX, XLSX, TXT, MD, JSON, YAML
    """
    start_time = time.time()
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        logger.info(f"Uploading document: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        import os
        import shutil
        from pathlib import Path
        
        upload_dir = Path(settings.DOCUMENT_UPLOAD_PATH)
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file.filename).name
        saved_path = upload_dir / safe_name
        if saved_path.exists():
            stem = saved_path.stem
            suffix = saved_path.suffix
            saved_path = upload_dir / f"{stem}_{int(time.time())}{suffix}"
        saved_path.write_bytes(content)
        
        # Ingest document
        result = rag_pipeline.ingest_documents([str(saved_path)])
        chunks_created = result.get('total_chunks', 0)
        execution_time = (time.time() - start_time) * 1000

        if chunks_created == 0:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"{file.filename} was saved but no retrieval chunks were created. "
                    "For PDFs, install pdfplumber and ensure the file has selectable text; "
                    "scanned PDFs require OCR before ingestion."
                )
            )

        return {
            "status": "success",
            "filename": file.filename,
            "saved_path": str(saved_path),
            "chunks_created": chunks_created,
            "execution_time_ms": execution_time,
            "message": "Document indexed successfully"
        }
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload error: {str(e)}"
        )


@router.post("/documents/batch-ingest", response_model=DocumentIngestResponse)
async def batch_ingest(request: BatchIngestRequest, background_tasks: BackgroundTasks):
    """
    Batch ingest documents from directory
    
    - **directory_path**: Path to documents directory
    - **recursive**: Process subdirectories
    - **file_extensions**: File types to process
    """
    start_time = time.time()
    
    try:
        import os
        from pathlib import Path
        
        if not os.path.isdir(request.directory_path):
            raise HTTPException(
                status_code=400,
                detail=f"Directory not found: {request.directory_path}"
            )
        
        logger.info(f"Starting batch ingest: {request.directory_path}")
        
        # Find files
        files = []
        path = Path(request.directory_path)
        
        if request.recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file():
                if any(file_path.suffix.lower() == ext for ext in request.file_extensions):
                    files.append(str(file_path))
        
        if not files:
            raise HTTPException(
                status_code=400,
                detail=f"No files found with extensions: {request.file_extensions}"
            )
        
        # Process files
        result = rag_pipeline.ingest_documents(files)
        
        execution_time = (time.time() - start_time) * 1000
        
        return DocumentIngestResponse(
            status="success",
            ingested_documents=len(files),
            failed_documents=result.get('failed_count', 0),
            total_chunks=result.get('total_chunks', 0),
            execution_time_ms=execution_time,
            details=[{"filename": f, "status": "success"} for f in files[:10]]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch ingest: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch ingest error: {str(e)}"
        )


@router.get("/documents/count")
async def document_count():
    """Get count of documents in knowledge base"""
    try:
        from app.core.vector_store import VectorStore
        vector_store = VectorStore()
        
        # Get collection stats
        collection = vector_store.collection
        count = collection.count()
        
        return {
            "status": "success",
            "document_count": count,
            "message": f"Knowledge base contains {count} documents"
        }
        
    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document count: {str(e)}"
        )


@router.get("/official-sources")
async def list_official_sources():
    """List curated official source entry points for SEBI/NSE/BSE/MCX ingestion."""
    return {
        "status": "success",
        "sources": official_sources.list_sources(),
        "message": "Download exact circular files from these official sources, then ingest with metadata."
    }


@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        from app.core.vector_store import VectorStore
        vector_store = VectorStore()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "documents_in_kb": vector_store.collection.count(),
                "vector_store_type": "Chroma",
                "embedding_model": "text-embedding-3-small",
                "llm_model": settings.OPENAI_MODEL
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )


@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Broking AI Assistant",
        "version": settings.PROJECT_VERSION,
        "description": "RAG-based AI assistant for Indian broking domain",
        "endpoints": {
            "health": "/health",
            "ask": "/ask",
            "search": "/search",
            "upload": "/documents/upload",
            "batch_ingest": "/documents/batch-ingest",
            "stats": "/stats"
        }
    }
