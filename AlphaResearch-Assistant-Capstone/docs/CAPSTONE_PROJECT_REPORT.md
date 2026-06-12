# Capstone Project Report: AlphaResearch Assistant

## 1. Executive Summary

AlphaResearch Assistant is a Gen AI and Agentic AI capstone project for Indian broking operations. It helps users ask questions about broking workflows, compliance requirements, exchange processes, settlement, KYC, margin trading, derivatives, DPDP, PMLA/AML, and related SOPs.

The project implements a Retrieval-Augmented Generation architecture where the assistant retrieves relevant knowledge from local documents and uploaded circulars, then generates a grounded and professionally formatted answer. The application includes a polished web interface, login screen, document upload, response feedback, chat history, and follow-up question handling.

## 2. Problem Statement

Broking operations teams handle a large volume of regulatory, process, and exchange-specific information. This knowledge is often spread across SOP documents, circulars, manuals, FAQs, and internal notes. Searching manually is slow, and generic LLM answers can be incomplete or unsupported.

The problem addressed by this project is:

> How can a broking firm provide a professional AI assistant that answers operational and compliance questions using trusted internal documents and official circular metadata?

## 3. Objectives

- Build a domain-specific AI assistant for Indian broking operations.
- Use RAG so answers are grounded in indexed documents.
- Support upload and ingestion of new circulars and SOP files.
- Provide official-source metadata fields for citation-ready answers.
- Deliver a professional, production-grade user interface.
- Support follow-up questions so the assistant can simplify or summarize previous responses.
- Provide Docker and local deployment options for portability.

## 4. Scope

The application focuses on:

- Broking SOPs and operational workflows.
- KYC, account opening, trading, settlement, margin, and risk processes.
- SEBI, NSE, BSE, MCX, DPDP, MTF, and PMLA/AML knowledge.
- Document ingestion and semantic retrieval.
- Chat-based knowledge assistant behavior.

Out of scope for the capstone:

- Real trading execution.
- Live market data integration.
- Production-grade authentication and authorization.
- Legal or investment advisory recommendations.
- Automated compliance certification.

## 5. Target Users

- Broking operations teams.
- Compliance and risk teams.
- Customer support teams.
- Training and knowledge-management teams.
- Students or evaluators reviewing a Gen AI capstone project.

## 6. Solution Overview

AlphaResearch Assistant has four major layers:

1. **Presentation Layer**: Static HTML, CSS, and JavaScript web UI served by FastAPI.
2. **API Layer**: FastAPI endpoints for chat, upload, search, stats, health, and official sources.
3. **RAG and Agent Layer**: Planner, retriever, reasoner, response generator, direct follow-up handling, and RAG pipeline.
4. **Knowledge Layer**: Markdown knowledge base, uploaded documents, ChromaDB vector store, and official-source metadata registry.

## 7. Technical Architecture

See [Technical Architecture](TECHNICAL_ARCHITECTURE.md).

The implementation-matching architecture diagram is included here:

![AlphaResearch Technical Architecture](assets/AlphaResearch_Technical_Architecture.svg)

The originally supplied reference image is preserved at `docs/assets/Technical_Architecture.png`. The implemented architecture differs from that reference image in a few important ways:

- The implemented UI uses FastAPI-served static HTML/CSS/JS, not Streamlit.
- The implemented LLM provider is OpenAI, not Gemini.
- The implemented embedding model is OpenAI `text-embedding-3-small`, with offline deterministic fallback.
- The implemented vector database is ChromaDB.
- The implemented backend is FastAPI.

## 8. Data Flow

1. User opens the web app at `http://127.0.0.1:8000`.
2. User logs in with demo credentials.
3. User asks a question or selects an SOP card.
4. Frontend sends the question, session ID, and recent conversation history to `POST /api/ask`.
5. Backend checks whether the query is a follow-up such as "summarize above in 10 lines".
6. If it is a direct follow-up, the backend rewrites the previous answer deterministically.
7. Otherwise, the agent orchestrator plans retrieval subtasks.
8. Retrieval service searches ChromaDB for semantically similar chunks.
9. Retrieved context and source metadata are passed to the LLM service.
10. The response is returned with answer, sources, confidence, retrieval summary, and execution time.
11. Frontend renders professional Markdown and allows the user to rate the answer.

## 9. Document Ingestion Flow

1. User uploads a supported document through the UI or runs batch ingestion.
2. Backend extracts text using file-specific parsers.
3. Text is split into overlapping semantic chunks.
4. Embeddings are generated.
5. Chunks and metadata are stored in ChromaDB.
6. Uploaded document content becomes searchable for future answers.

Supported file types:

- PDF
- DOCX
- XLSX
- CSV
- TXT
- Markdown
- JSON
- YAML

If a PDF is scanned or image-only, OCR is required before ingestion.

## 10. Agentic AI Components

The app includes a lightweight multi-agent design:

- **Planner Agent**: Classifies the query and creates subtasks.
- **Retriever Agent**: Retrieves relevant chunks for the main query and subtasks.
- **Reasoning Agent**: Checks retrieved documents and identifies key insights or gaps.
- **Response Agent**: Generates a polished answer using the retrieved context.

This demonstrates agentic orchestration without adding unnecessary complexity for a capstone project.

## 11. RAG Components

- **Chunking**: `app/core/text_chunking.py`
- **Embeddings**: `app/core/embeddings.py`
- **Vector Store**: `app/core/vector_store.py`
- **Retrieval Service**: `app/services/retrieval_service.py`
- **RAG Pipeline**: `app/core/rag_pipeline.py`
- **LLM Service**: `app/services/llm_service.py`

## 12. UI/UX Features

- Teal-focused professional branding.
- Alpha symbol logo.
- Login screen with visible demo credentials.
- SOP cards for fast task discovery.
- Chat assistant with Enter-to-submit.
- Upload action in the top-right utility area.
- Icon-only logout button.
- Clear chat button.
- Response rating with interactive acknowledgement.
- Rich Markdown rendering for headings, bullets, numbered lists, and source sections.

## 13. Knowledge Base and Sources

The project contains curated markdown knowledge in `knowledge-base/`, including:

- `SOPs.md`
- `SEBI_Regulations.md`
- `NSE_Trading_Guide.md`
- `BSE_Overview.md`
- `MCX_Commodities_Guide.md`
- `Official_MTF_Guide.md`
- `Official_DPDP_Guide.md`
- `Official_PMLA_AML_Guide.md`
- `Process_Manuals.md`
- `FAQs.md`

The official source registry is stored in `data/official_sources.json`.

## 14. Environment Configuration

Important environment variables:

```env
APP_NAME=AlphaResearch Assistant
APP_VERSION=1.0.0
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DB_PATH=./data/embeddings/chroma_db
CHROMA_COLLECTION_NAME=broking_knowledge_base
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.6
```

## 15. Local Execution

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.scripts.ingest_documents --source ./knowledge-base
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## 16. Docker Execution

```powershell
copy .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Open `http://127.0.0.1:8000`.

## 17. Testing Performed

The application was tested for:

- App launch and health endpoint.
- Knowledge base ingestion.
- Document upload and zero-chunk handling.
- Chat question answering.
- Follow-up prompts such as "summarize above in 10 lines".
- Markdown rendering with numbered lists.
- UI login and logout flow.
- Clear chat behavior.
- Response rating interaction.

## 18. Risks and Limitations

- Demo login is not production authentication.
- Generated responses depend on the quality and freshness of ingested documents.
- Uploaded scanned PDFs need OCR before indexing.
- Official circular ingestion requires correct source metadata.
- The assistant should not be used as legal, tax, investment, or regulatory approval advice.

## 19. Future Enhancements

- Server-side authentication with RBAC.
- Admin dashboard for source governance.
- OCR pipeline for scanned circulars.
- Scheduled ingestion from official SEBI/NSE/BSE/MCX sources.
- Answer-level citation highlighting.
- Evaluation dataset and automated answer-quality scoring.
- Langfuse or OpenTelemetry-based tracing.
- Cloud deployment with CI/CD.

## 20. Conclusion

AlphaResearch Assistant demonstrates an end-to-end Gen AI and Agentic AI application for a practical regulated-domain use case. It shows document ingestion, semantic retrieval, LLM response generation, source metadata, follow-up memory, and a professional user experience suitable for a capstone submission.
