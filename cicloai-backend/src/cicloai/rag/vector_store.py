from __future__ import annotations

# ruff: noqa: E402

import os

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings
from openai import OpenAI

from cicloai.rag.config import RagConfig
from cicloai.rag.text_splitter import TextChunk


class KnowledgeBaseNotIndexedError(RuntimeError):
    pass


class VectorStore:
    """Persistent Chroma vector store backed by OpenAI embeddings."""

    _COLLECTION_NAME = "cicloai_convocatoria"

    def __init__(self, config: RagConfig) -> None:
        self._config = config
        self._client = chromadb.PersistentClient(
            path=str(config.vector_store_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            self._COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._openai = OpenAI(api_key=config.openai_api_key)

    def rebuild(self, chunks: list[TextChunk]) -> None:
        if not self._config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY no está configurada.")
        if not chunks:
            raise RuntimeError("No hay documentos para indexar.")

        try:
            self._client.delete_collection(self._COLLECTION_NAME)
        except ValueError:
            pass
        self._collection = self._client.get_or_create_collection(
            self._COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        embeddings = self._embed([chunk.text for chunk in chunks])
        self._collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=embeddings,
        )

    def query(self, question: str, top_k: int) -> list[dict]:
        if self._collection.count() == 0:
            raise KnowledgeBaseNotIndexedError(
                "La base de conocimiento no está indexada. Ejecute python -m cicloai.rag.index_documents"
            )

        embedding = self._embed([question])[0]
        result = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        rows: list[dict] = []
        for index, chunk_id in enumerate(result.get("ids", [[]])[0]):
            distance = result.get("distances", [[]])[0][index]
            rows.append(
                {
                    "chunk_id": chunk_id,
                    "text": result.get("documents", [[]])[0][index],
                    "metadata": result.get("metadatas", [[]])[0][index],
                    "score": max(0.0, 1.0 - float(distance)),
                }
            )
        return rows

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[dict]:
        if not chunk_ids:
            return []

        result = self._collection.get(ids=chunk_ids)
        rows: list[dict] = []
        for index, chunk_id in enumerate(result.get("ids", [])):
            rows.append(
                {
                    "chunk_id": chunk_id,
                    "text": result.get("documents", [])[index],
                    "metadata": result.get("metadatas", [])[index],
                    "score": 0.0,
                }
            )
        return rows

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if not self._config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY no está configurada.")
        response = self._openai.embeddings.create(
            model=self._config.embedding_model, input=texts
        )
        return [item.embedding for item in response.data]
