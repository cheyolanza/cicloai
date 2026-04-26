from cicloai.application.chunking import TextChunker
from cicloai.application.ingest_service import IngestService
from cicloai.application.query_service import QueryService
from cicloai.infrastructure.llm.extractive_llm import ExtractiveLLMClient
from cicloai.infrastructure.repositories.json_document_repository import JsonDocumentRepository
from cicloai.infrastructure.vector_store.hash_vector_store import HashVectorStore


def test_ingest_and_query_pipeline(tmp_path) -> None:
    repository = JsonDocumentRepository(tmp_path / "documents.json")
    vector_index = HashVectorStore(tmp_path / "vectors.json", dimensions=64)
    ingest_service = IngestService(repository, vector_index, TextChunker(chunk_size=30, overlap=5))
    query_service = QueryService(vector_index, ExtractiveLLMClient(), default_top_k=2)

    ingest_result = ingest_service.ingest(
        "CicloAI valida pagos con OCR y compara el monto detectado contra el monto esperado.",
        metadata={"source": "test"},
    )
    answer = query_service.query("Como valida pagos CicloAI?")

    assert ingest_result["chunks_indexed"] == 1
    assert "OCR" in answer.answer or "ocr" in answer.answer
    assert answer.sources
    assert answer.sources[0].score > 0

