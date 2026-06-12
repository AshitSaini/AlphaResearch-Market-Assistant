"""Bulk ingest documents into the local vector store.

Usage:
    python -m app.scripts.ingest_documents --source ./knowledge-base
"""
import argparse
import json
from pathlib import Path

from app.core.rag_pipeline import RAGPipeline


DEFAULT_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".xlsx", ".json", ".yaml", ".yml"}


def discover_files(source: Path, recursive: bool) -> list[str]:
    """Return supported files under a file or directory source."""
    if source.is_file():
        return [str(source)] if source.suffix.lower() in DEFAULT_EXTENSIONS else []

    pattern = "**/*" if recursive else "*"
    return [
        str(path)
        for path in source.glob(pattern)
        if path.is_file() and path.suffix.lower() in DEFAULT_EXTENSIONS
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest knowledge-base documents.")
    parser.add_argument("--source", default="./knowledge-base", help="File or directory to ingest")
    parser.add_argument("--no-recursive", action="store_true", help="Only ingest direct children")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    files = discover_files(source, recursive=not args.no_recursive)
    if not files:
        raise SystemExit(f"No supported documents found in {source}")

    pipeline = RAGPipeline()
    result = pipeline.ingest_documents(files)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
