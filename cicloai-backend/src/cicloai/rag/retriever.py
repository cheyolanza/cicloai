from __future__ import annotations

import re

from cicloai.rag.config import RagConfig
from cicloai.rag.vector_store import VectorStore


class Retriever:
    """Retrieves convocatoria chunks and applies a similarity threshold."""

    def __init__(self, vector_store: VectorStore, config: RagConfig) -> None:
        self._vector_store = vector_store
        self._config = config

    def retrieve(self, question: str) -> list[dict]:
        rows = self._vector_store.query(question, top_k=self._config.top_k)
        rows = self._with_neighbor_chunks(rows)
        filtered_rows = [row for row in rows if row["score"] >= self._config.similarity_threshold]
        if filtered_rows:
            return filtered_rows

        # Short natural-language questions can score below the configured
        # threshold even when the top chunks are clearly from the right
        # convocatoria section. Falling back to the best retrieved chunks avoids
        # false "No tengo información" answers while the prompt still prevents
        # unsupported claims.
        return self._in_document_order(rows)

    def _with_neighbor_chunks(self, rows: list[dict]) -> list[dict]:
        """Adds adjacent chunks so long lists are not cut mid-section."""

        neighbor_ids: list[str] = []
        for row in rows:
            chunk_id = str(row["chunk_id"])
            match = re.match(r"(.+:\d+:)(\d+)$", chunk_id)
            if not match:
                continue
            prefix, index_text = match.groups()
            index = int(index_text)
            if index > 0:
                neighbor_ids.append(f"{prefix}{index - 1}")
            neighbor_ids.append(f"{prefix}{index + 1}")

        existing_ids = {str(row["chunk_id"]) for row in rows}
        missing_neighbor_ids = [chunk_id for chunk_id in dict.fromkeys(neighbor_ids) if chunk_id not in existing_ids]
        neighbors = self._vector_store.get_chunks_by_ids(missing_neighbor_ids)

        combined = rows + neighbors
        deduped: dict[str, dict] = {}
        for row in combined:
            deduped.setdefault(str(row["chunk_id"]), row)
        return list(deduped.values())

    def _in_document_order(self, rows: list[dict]) -> list[dict]:
        def sort_key(row: dict) -> tuple[str, int, int]:
            chunk_id = str(row["chunk_id"])
            match = re.match(r"(.+):(\d+):(\d+)$", chunk_id)
            if not match:
                return (chunk_id, 0, 0)
            source, page, index = match.groups()
            return (source, int(page), int(index))

        return sorted(rows, key=sort_key)
