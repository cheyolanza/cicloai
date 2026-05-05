from __future__ import annotations

import json
import math
from hashlib import sha256
from pathlib import Path

from cicloai.application.chunking import tokenize
from cicloai.domain.entities import Chunk, RetrievedChunk


class HashVectorStore:
    def __init__(self, storage_path: Path, dimensions: int = 384) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")

        self.storage_path = storage_path
        self.dimensions = dimensions
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]", encoding="utf-8")

    def add_chunks(self, chunks: list[Chunk]) -> None:
        records = self._load()
        existing_ids = {record["chunk"]["chunk_id"] for record in records}

        for chunk in chunks:
            if chunk.chunk_id in existing_ids:
                continue
            existing_ids.add(chunk.chunk_id)
            records.append(
                {
                    "chunk": {
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                    },
                    "embedding": self._embed(chunk.text),
                }
            )

        self._dump(records)

    def search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if top_k <= 0:
            return []

        query_embedding = self._embed(query)
        scored: list[RetrievedChunk] = []

        for record in self._load():
            chunk_payload = record["chunk"]
            chunk = Chunk(
                chunk_id=chunk_payload["chunk_id"],
                document_id=chunk_payload["document_id"],
                text=chunk_payload["text"],
                metadata=chunk_payload.get("metadata", {}),
            )
            score = self._cosine(query_embedding, record["embedding"])
            if score > 0:
                scored.append(RetrievedChunk(chunk=chunk, score=round(score, 4)))

        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    def count(self) -> int:
        return len(self._load())

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            index = int(sha256(token.encode("utf-8")).hexdigest(), 16) % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        return sum(
            left_value * right_value for left_value, right_value in zip(left, right)
        )

    def _load(self) -> list[dict]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _dump(self, records: list[dict]) -> None:
        self.storage_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
        )
