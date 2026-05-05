from __future__ import annotations

import json

import pytest

from cicloai.domain.entities import Chunk
from cicloai.infrastructure.vector_store.hash_vector_store import HashVectorStore


def test_vector_store_creates_storage_file_and_counts_chunks(tmp_path) -> None:
    store = HashVectorStore(tmp_path / "vectors" / "index.json", dimensions=16)

    assert store.count() == 0
    assert json.loads(store.storage_path.read_text(encoding="utf-8")) == []


def test_vector_store_indexes_chunks_and_skips_duplicates(tmp_path) -> None:
    store = HashVectorStore(tmp_path / "index.json", dimensions=32)
    chunk = Chunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="inscripcion masiva excel",
        metadata={"source": "rules"},
    )

    store.add_chunks([chunk, chunk])

    assert store.count() == 1
    records = json.loads(store.storage_path.read_text(encoding="utf-8"))
    assert records[0]["chunk"]["metadata"] == {"source": "rules"}


def test_vector_store_search_returns_ranked_matches(tmp_path) -> None:
    store = HashVectorStore(tmp_path / "index.json", dimensions=128)
    store.add_chunks(
        [
            Chunk("a", "doc", "pago qr monto comprobante", {}),
            Chunk("b", "doc", "categoria federado master", {}),
            Chunk("c", "doc", "pago validado banco union", {}),
        ]
    )

    results = store.search("pago banco", top_k=2)

    assert [result.chunk.chunk_id for result in results] == ["c", "a"]
    assert results[0].score >= results[1].score > 0


def test_vector_store_search_returns_empty_for_no_results_or_invalid_limit(
    tmp_path,
) -> None:
    store = HashVectorStore(tmp_path / "index.json", dimensions=16)
    store.add_chunks([Chunk("a", "doc", "categoria master", {})])

    assert store.search("zzzzzz", top_k=5) == []
    assert store.search("categoria", top_k=0) == []


def test_vector_store_rejects_invalid_dimensions(tmp_path) -> None:
    with pytest.raises(ValueError, match="dimensions"):
        HashVectorStore(tmp_path / "index.json", dimensions=0)
