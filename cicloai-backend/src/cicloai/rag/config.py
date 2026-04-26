from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cicloai.infrastructure.config import Settings


@dataclass(frozen=True)
class RagConfig:
    documents_dir: Path
    vector_store_dir: Path
    openai_api_key: str
    chat_model: str
    embedding_model: str
    top_k: int
    similarity_threshold: float
    chunk_size: int
    chunk_overlap: int


def build_rag_config(settings: Settings) -> RagConfig:
    return RagConfig(
        documents_dir=settings.rag_documents_dir,
        vector_store_dir=settings.rag_vector_store_dir,
        openai_api_key=settings.openai_api_key,
        chat_model=settings.openai_model,
        embedding_model=settings.openai_embedding_model,
        top_k=settings.rag_top_k,
        similarity_threshold=settings.rag_similarity_threshold,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )
