from __future__ import annotations

from dataclasses import dataclass

from cicloai.rag.document_loader import LoadedDocument


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    text: str
    metadata: dict[str, str]


class TextSplitter:
    """Character splitter tuned for short convocatoria documents.

    800 chars keeps enough rule context in each chunk; 150 chars overlap
    preserves category/cost sentences that may cross chunk boundaries.
    """

    def __init__(self, chunk_size: int, overlap: int) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def split(self, documents: list[LoadedDocument]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        for document in documents:
            text = " ".join(document.text.split())
            start = 0
            chunk_number = 0
            while start < len(text):
                chunk_text = text[start : start + self._chunk_size]
                if chunk_text.strip():
                    chunk_number += 1
                    source = document.metadata["source_file"]
                    chunks.append(
                        TextChunk(
                            chunk_id=f"{source}:{document.metadata.get('page', '0')}:{chunk_number}",
                            text=chunk_text,
                            metadata={
                                **document.metadata,
                                "chunk_id": f"{source}:{document.metadata.get('page', '0')}:{chunk_number}",
                            },
                        )
                    )
                start += self._chunk_size - self._overlap
        return chunks
