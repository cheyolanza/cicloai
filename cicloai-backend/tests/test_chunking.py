from cicloai.application.chunking import TextChunker
from cicloai.domain.entities import Document


def test_chunker_splits_with_overlap() -> None:
    text = " ".join(f"token{i}" for i in range(30))
    chunker = TextChunker(chunk_size=10, overlap=2)

    chunks = chunker.split(Document(document_id="doc_test", text=text))

    assert len(chunks) == 4
    assert chunks[0].document_id == "doc_test"
    assert chunks[0].metadata["chunk_index"] == "0"


def test_chunker_ignores_blank_text() -> None:
    chunker = TextChunker()

    chunks = chunker.split(Document(document_id="doc_blank", text="   "))

    assert chunks == []
