from __future__ import annotations

import unicodedata
from typing import Literal

AgentIntent = Literal[
    "rag_answer", "start_single_registration", "start_bulk_registration"
]


class IntentDetectionService:
    """Rule-based operational intent detector kept separate from RAG."""

    _single_phrases = (
        "quiero inscribirme",
        "deseo inscribirme",
        "quiero registrarme",
        "inscribirme a la carrera",
        "inscripcion unitaria",
        "inscripción unitaria",
    )
    _bulk_phrases = (
        "quiero inscribir a mi equipo",
        "quiero inscribir varios",
        "quiero inscribir a todos",
        "inscripcion masiva",
        "inscripción masiva",
        "registrar varios ciclistas",
        "cargar excel",
    )

    def detect(self, message: str) -> AgentIntent:
        normalized = self._normalize(message)
        if any(self._normalize(phrase) in normalized for phrase in self._bulk_phrases):
            return "start_bulk_registration"
        if any(
            self._normalize(phrase) in normalized for phrase in self._single_phrases
        ):
            return "start_single_registration"
        return "rag_answer"

    def _normalize(self, value: str) -> str:
        text = unicodedata.normalize("NFKD", value.lower())
        return "".join(
            character for character in text if not unicodedata.combining(character)
        )
