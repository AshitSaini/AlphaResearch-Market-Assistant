"""Official source registry and ingestion helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from app.services.document_service import DocumentService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_SOURCE_REGISTRY = PROJECT_ROOT / "data" / "official_sources.json"


class OfficialSourceService:
    """Load curated official exchange/regulator source metadata."""

    def __init__(self, registry_path: Path = OFFICIAL_SOURCE_REGISTRY):
        self.registry_path = registry_path

    def list_sources(self) -> List[Dict]:
        if not self.registry_path.exists():
            return []
        with self.registry_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def find_source(self, title: str) -> Dict:
        title_normalized = title.strip().lower()
        for source in self.list_sources():
            if source.get("title", "").strip().lower() == title_normalized:
                return source
        raise ValueError(f"Official source not found: {title}")

    def build_document_from_file(self, file_path: str, metadata: Dict) -> Dict:
        """Create a RAG document object from a downloaded official file."""
        path = Path(file_path)
        text = DocumentService.ingest(str(path))
        return {
            "id": metadata.get("title") or path.name,
            "text": text,
            "metadata": {
                "source": metadata.get("title") or path.name,
                "source_url": metadata.get("source_url", ""),
                "circular_no": metadata.get("circular_no", ""),
                "date": metadata.get("date", ""),
                "exchange": metadata.get("exchange", ""),
                "section": metadata.get("section", ""),
                "category": metadata.get("category", "official"),
                "path": str(path),
            },
        }
