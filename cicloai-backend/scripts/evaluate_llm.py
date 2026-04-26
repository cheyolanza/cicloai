#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from cicloai.application.chunking import TextChunker, tokenize
from cicloai.application.ingest_service import IngestService
from cicloai.application.query_service import QueryService
from cicloai.infrastructure.llm.extractive_llm import ExtractiveLLMClient
from cicloai.infrastructure.repositories.json_document_repository import JsonDocumentRepository
from cicloai.infrastructure.vector_store.hash_vector_store import HashVectorStore


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))



DATASET = [
    {
        "question": "Como inicia el flujo de CicloAI?",
        "expected_terms": {"humanidad", "correo", "validacion"},
        "source": "flujo-general",
    },
    {
        "question": "Que se valida en una inscripcion masiva?",
        "expected_terms": {"excel", "equipo", "categorias"},
        "source": "flujo-masivo",
    },
    {
        "question": "Como se valida el pago?",
        "expected_terms": {"ocr", "monto", "participantes"},
        "source": "pagos",
    },
]

DOCUMENTS = [
    (
        "flujo-general",
        "El flujo de CicloAI inicia con validacion de humanidad y validacion de correo electronico antes de crear una sesion.",
    ),
    (
        "flujo-masivo",
        "La inscripcion masiva carga un archivo Excel, valida que los participantes pertenezcan al mismo equipo y revisa categorias validas.",
    ),
    (
        "pagos",
        "CicloAI analiza el comprobante de pago con OCR y compara el monto detectado contra el monto esperado por numero de participantes.",
    ),
]


def term_recall(answer: str, expected_terms: set[str]) -> float:
    answer_terms = set(tokenize(answer))
    matches = expected_terms.intersection(answer_terms)
    return len(matches) / len(expected_terms)


def groundedness(answer: str, source_texts: list[str]) -> float:
    answer_terms = set(tokenize(answer))
    context_terms = set(tokenize(" ".join(source_texts)))
    if not answer_terms:
        return 0.0
    return len(answer_terms.intersection(context_terms)) / len(answer_terms)


def main() -> None:
    runtime_dir = ROOT / "tmp" / "evaluation"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    repository = JsonDocumentRepository(runtime_dir / "documents.json")
    vector_index = HashVectorStore(runtime_dir / "vectors.json")
    ingest_service = IngestService(repository, vector_index, TextChunker(chunk_size=80, overlap=10))
    query_service = QueryService(vector_index, ExtractiveLLMClient(), default_top_k=2)

    for source, text in DOCUMENTS:
        ingest_service.ingest(text, metadata={"source": source}, document_id=f"eval_{source}")

    rows = []
    for item in DATASET:
        response = query_service.query(item["question"], top_k=2)
        source_texts = [source.chunk.text for source in response.sources]
        top_source = response.sources[0].chunk.metadata.get("source") if response.sources else None
        rows.append(
            {
                "question": item["question"],
                "answer": response.answer,
                "latency_ms": response.latency_ms,
                "term_recall": round(term_recall(response.answer, item["expected_terms"]), 3),
                "context_precision_at_1": 1.0 if top_source == item["source"] else 0.0,
                "groundedness": round(groundedness(response.answer, source_texts), 3),
            }
        )

    summary = {
        "samples": len(rows),
        "avg_latency_ms": round(statistics.mean(row["latency_ms"] for row in rows), 2),
        "avg_term_recall": round(statistics.mean(row["term_recall"] for row in rows), 3),
        "context_precision_at_1": round(statistics.mean(row["context_precision_at_1"] for row in rows), 3),
        "avg_groundedness": round(statistics.mean(row["groundedness"] for row in rows), 3),
    }

    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "evaluation_llm.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (reports_dir / "evaluation_llm.md").write_text(render_markdown(summary, rows), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def render_markdown(summary: dict, rows: list[dict]) -> str:
    lines = [
        "# Reporte de Evaluacion LLM/RAG",
        "",
        "## Metricas",
        "",
        f"- Muestras evaluadas: {summary['samples']}",
        f"- Latencia promedio: {summary['avg_latency_ms']} ms",
        f"- Term recall promedio: {summary['avg_term_recall']}",
        f"- Context precision@1: {summary['context_precision_at_1']}",
        f"- Groundedness promedio: {summary['avg_groundedness']}",
        "",
        "## Resultados por consulta",
        "",
        "| Pregunta | Term Recall | Precision@1 | Groundedness | Latencia ms |",
        "|----------|-------------|-------------|--------------|-------------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['question']} | {row['term_recall']} | {row['context_precision_at_1']} | "
            f"{row['groundedness']} | {row['latency_ms']} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

