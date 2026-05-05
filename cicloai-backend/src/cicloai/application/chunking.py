from __future__ import annotations

import re
from hashlib import sha256

from cicloai.domain.entities import Chunk, Document


TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


class TextChunker:
    def __init__(self, chunk_size: int = 120, overlap: int = 25) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be >= 0 and lower than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, document: Document) -> list[Chunk]:
        tokens = tokenize(document.text)
        if not tokens:
            return []

        chunks: list[Chunk] = []
        step = self.chunk_size - self.overlap
        for index, start in enumerate(range(0, len(tokens), step)):
            window = tokens[start : start + self.chunk_size]
            if not window:
                continue

            text = " ".join(window)
            digest = sha256(
                f"{document.document_id}:{index}:{text}".encode("utf-8")
            ).hexdigest()[:16]
            chunks.append(
                Chunk(
                    chunk_id=f"chk_{digest}",
                    document_id=document.document_id,
                    text=text,
                    metadata={**document.metadata, "chunk_index": str(index)},
                )
            )

            if start + self.chunk_size >= len(tokens):
                break

        return chunks
