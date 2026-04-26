from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from cicloai.domain.entities import Document


class JsonDocumentRepository:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def save(self, document: Document) -> None:
        payload = self._load()
        document_payload = asdict(document)
        document_payload["created_at"] = document.created_at.isoformat()
        payload[document.document_id] = document_payload
        self._dump(payload)

    def get(self, document_id: str) -> Document | None:
        payload = self._load().get(document_id)
        if payload is None:
            return None
        return self._to_document(payload)

    def list(self) -> list[Document]:
        return [self._to_document(payload) for payload in self._load().values()]

    def _load(self) -> dict:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _dump(self, payload: dict) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _to_document(payload: dict) -> Document:
        return Document(
            document_id=payload["document_id"],
            text=payload["text"],
            metadata=payload.get("metadata", {}),
            created_at=datetime.fromisoformat(payload["created_at"]),
        )

