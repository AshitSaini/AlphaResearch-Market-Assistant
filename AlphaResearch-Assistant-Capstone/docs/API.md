# API Reference

Base URL: `http://localhost:8000`

## Health

`GET /health` and `GET /api/health`

Returns service status, version, timestamp, and core subsystem labels.

## Ask

`POST /api/ask`

```json
{
  "question": "What is KYC and why is it mandatory?",
  "enable_reasoning": true,
  "top_k": 5
}
```

Returns a grounded answer, confidence score, retrieval summary, execution time, and status.

## Search

`GET /api/search?query=settlement&limit=5&threshold=0.3`

`POST /api/search`

```json
{
  "query": "settlement",
  "top_k": 5,
  "threshold": 0.3
}
```

Returns relevant knowledge chunks with source metadata and similarity scores.

## Upload

`POST /api/documents/upload`

Multipart form with a `file` field. Supported formats include Markdown, text, PDF, DOCX, XLSX, JSON, and YAML when dependencies are installed.

## Batch Ingest

`POST /api/documents/batch-ingest`

```json
{
  "directory_path": "./knowledge-base",
  "recursive": true,
  "file_extensions": [".md", ".txt"]
}
```

## Stats

`GET /api/stats`

Returns vector-store count, embedding model, and LLM model configuration.

## Official Sources

`GET /api/official-sources`

Lists curated official SEBI/NSE/BSE/MCX entry points and metadata fields used for circular-grade ingestion.

## Ingest Official Circular Files

Download the exact official PDF or document first, then ingest it with provenance metadata:

```bash
python -m app.scripts.ingest_official_file \
  --file ./data/documents/sebi-master-circular.pdf \
  --title "SEBI Master Circular for Stock Brokers" \
  --exchange SEBI \
  --date 2024-05-22 \
  --circular-no "Master Circular" \
  --section "Stock Brokers" \
  --source-url "https://www.sebi.gov.in/legal/master-circulars/may-2024/master-circular-for-stock-brokers_83521.html"
```

When these fields are present, retrieved sources are cited with exchange, circular number, date, section, and URL instead of only a local filename.
