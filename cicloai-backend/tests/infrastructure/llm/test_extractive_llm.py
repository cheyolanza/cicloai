from __future__ import annotations

from cicloai.domain.entities import Chunk, RetrievedChunk
from cicloai.infrastructure.llm.extractive_llm import ExtractiveLLMClient


def retrieved(text: str, score: float = 1.0) -> RetrievedChunk:
    return RetrievedChunk(chunk=Chunk("chunk", "doc", text, {}), score=score)


def test_extractive_llm_returns_fallback_when_context_is_empty() -> None:
    answer = ExtractiveLLMClient().generate("inscripcion", [])

    assert "No tengo informacion suficiente" in answer


def test_extractive_llm_selects_best_sentence_per_context() -> None:
    answer = ExtractiveLLMClient().generate(
        "pago comprobante",
        [
            retrieved(
                "Las categorias se asignan por edad. El pago requiere comprobante QR."
            ),
            retrieved(
                "El comprobante se valida contra monto y banco. Otra frase sin relacion."
            ),
        ],
    )

    assert answer == (
        "Segun la base de conocimiento de CicloAI: "
        "El pago requiere comprobante QR. "
        "El comprobante se valida contra monto y banco"
    )


def test_extractive_llm_uses_chunk_text_when_sentences_are_blank() -> None:
    answer = ExtractiveLLMClient().generate("algo", [retrieved("   ")])

    assert answer == "Segun la base de conocimiento de CicloAI:    "
