"""Ingest an official circular file with source provenance metadata.

Example:
    python -m app.scripts.ingest_official_file --file ./data/documents/sebi.pdf \
      --title "SEBI Master Circular for Stock Brokers" \
      --exchange SEBI --date 2024-05-22 \
      --circular-no "Master Circular" \
      --source-url "https://www.sebi.gov.in/..."
"""
import argparse
import json

from app.core.rag_pipeline import RAGPipeline
from app.services.official_source_service import OfficialSourceService


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest an official file with citation metadata.")
    parser.add_argument("--file", required=True, help="Downloaded official PDF/DOCX/TXT/MD file")
    parser.add_argument("--title", required=True, help="Document title shown in citations")
    parser.add_argument("--exchange", required=True, help="SEBI/NSE/BSE/MCX")
    parser.add_argument("--date", default="", help="Circular date in YYYY-MM-DD")
    parser.add_argument("--circular-no", default="", help="Circular or notice number")
    parser.add_argument("--source-url", required=True, help="Official URL")
    parser.add_argument("--section", default="", help="Relevant section/topic")
    parser.add_argument("--category", default="official", help="Metadata category")
    args = parser.parse_args()

    metadata = {
        "title": args.title,
        "exchange": args.exchange,
        "date": args.date,
        "circular_no": args.circular_no,
        "source_url": args.source_url,
        "section": args.section,
        "category": args.category,
    }
    document = OfficialSourceService().build_document_from_file(args.file, metadata)
    result = RAGPipeline().ingest_documents([document])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
