from __future__ import annotations

from typing import Protocol

from cicloai.domain.entities import Chunk, Document, RetrievedChunk


class DocumentRepository(Protocol):
    def save(self, document: Document) -> None:
        ...

    def get(self, document_id: str) -> Document | None:
        ...

    def list(self) -> list[Document]:
        ...


class VectorIndex(Protocol):
    def add_chunks(self, chunks: list[Chunk]) -> None:
        ...

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        ...

    def count(self) -> int:
        ...


class LLMClient(Protocol):
    model_name: str

    def generate(self, query: str, contexts: list[RetrievedChunk]) -> str:
        ...

