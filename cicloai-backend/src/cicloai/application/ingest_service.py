from __future__ import annotations

from hashlib import sha256

from cicloai.application.chunking import TextChunker
from cicloai.domain.entities import Document
from cicloai.domain.ports import DocumentRepository, VectorIndex


class IngestService:
    def __init__(
        self,
        repository: DocumentRepository,
        vector_index: VectorIndex,
        chunker: TextChunker,
    ) -> None:
        self.repository = repository
        self.vector_index = vector_index
        self.chunker = chunker

    def ingest(
        self,
        text: str,
        metadata: dict[str, str] | None = None,
        document_id: str | None = None,
    ) -> dict:
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("text is required")

        resolved_document_id = document_id or self._build_document_id(
            clean_text, metadata or {}
        )
        document = Document(
            document_id=resolved_document_id, text=clean_text, metadata=metadata or {}
        )
        chunks = self.chunker.split(document)

        self.repository.save(document)
        self.vector_index.add_chunks(chunks)

        return {
            "document_id": document.document_id,
            "chunks_indexed": len(chunks),
            "metadata": document.metadata,
        }

    @staticmethod
    def _build_document_id(text: str, metadata: dict[str, str]) -> str:
        source = metadata.get("source", "")
        digest = sha256(f"{source}:{text}".encode("utf-8")).hexdigest()[:16]
        return f"doc_{digest}"
