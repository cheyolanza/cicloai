from __future__ import annotations

import pytest

from cicloai.application.chunking import TextChunker, tokenize
from cicloai.domain.entities import Document


def test_tokenize_normalizes_case_and_punctuation() -> None:
    assert tokenize("CicloAI, MTB 2026!") == ["cicloai", "mtb", "2026"]


def test_chunker_returns_empty_list_for_empty_text() -> None:
    assert TextChunker().split(Document(document_id="empty", text="\n\t ")) == []


def test_chunker_keeps_short_text_in_single_chunk_with_metadata() -> None:
    document = Document(
        document_id="rules", text="Inscripcion valida", metadata={"source": "unit"}
    )

    chunks = TextChunker(chunk_size=10, overlap=2).split(document)

    assert len(chunks) == 1
    assert chunks[0].text == "inscripcion valida"
    assert chunks[0].metadata == {"source": "unit", "chunk_index": "0"}
    assert chunks[0].chunk_id.startswith("chk_")


def test_chunker_splits_long_text_with_overlap_and_stable_ids() -> None:
    document = Document(
        document_id="long", text=" ".join(f"token{i}" for i in range(12))
    )
    chunker = TextChunker(chunk_size=5, overlap=2)

    chunks = chunker.split(document)
    repeated = chunker.split(document)

    assert [chunk.text for chunk in chunks] == [
        "token0 token1 token2 token3 token4",
        "token3 token4 token5 token6 token7",
        "token6 token7 token8 token9 token10",
        "token9 token10 token11",
    ]
    assert [chunk.chunk_id for chunk in chunks] == [
        chunk.chunk_id for chunk in repeated
    ]


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (5, -1), (5, 5), (5, 8)],
)
def test_chunker_rejects_invalid_configuration(chunk_size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        TextChunker(chunk_size=chunk_size, overlap=overlap)
