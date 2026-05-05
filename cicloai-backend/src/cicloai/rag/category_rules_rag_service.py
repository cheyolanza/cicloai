from __future__ import annotations

from dataclasses import dataclass
import re

from openai import OpenAI

from cicloai.infrastructure.config import Settings
from cicloai.rag.prompt_builder import PromptBuilder


@dataclass(frozen=True)
class CategoryDetectionPromptData:
    birth_date: str
    age: int
    declared_category: str
    gender: str | None
    date_of_race: str


class CategoryRulesRagService:
    """RAG boundary specialized in category detection from convocatoria rules.

    The service reads the configured convocatoria text, retrieves relevant
    chunks for the declared rider type, and asks OpenAI for a strictly
    constrained category name. It is intentionally independent from the
    registration use case so tests can replace it with a mock.
    """

    def __init__(
        self, settings: Settings, prompt_builder: PromptBuilder | None = None
    ) -> None:
        self._settings = settings
        self._prompt_builder = prompt_builder or PromptBuilder()

    def detect_category(self, data: CategoryDetectionPromptData) -> str:
        if self._settings.enable_rag_mock:
            return self._detect_with_mock(data)

        if not self._settings.openai_api_key:
            return "NO_DETERMINADA"

        context = self._retrieve_context(data)
        if not context:
            return "NO_DETERMINADA"

        messages = self._prompt_builder.build_category_detection_messages(
            context=context,
            birth_date=data.birth_date,
            age=data.age,
            declared_category=data.declared_category,
            gender=data.gender,
            date_of_race=data.date_of_race,
        )
        response = OpenAI(
            api_key=self._settings.openai_api_key
        ).chat.completions.create(
            model=self._settings.openai_model,
            messages=messages,
            temperature=0,
        )
        return (response.choices[0].message.content or "").strip()

    def _retrieve_context(self, data: CategoryDetectionPromptData) -> str:
        document_path = self._settings.category_rules_pdf_path
        if not document_path.exists() or not document_path.is_file():
            return ""

        text = document_path.read_text(encoding="utf-8", errors="ignore")
        chunks = self._split_text(text)
        keywords = self._keywords_for(data)
        scored_chunks = sorted(
            ((self._score_chunk(chunk, keywords), chunk) for chunk in chunks),
            key=lambda item: item[0],
            reverse=True,
        )
        selected = [chunk for score, chunk in scored_chunks if score > 0][
            : self._settings.rag_top_k
        ]
        if not selected:
            selected = chunks[: self._settings.rag_top_k]
        return "\n\n".join(selected)

    def _split_text(self, text: str) -> list[str]:
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]
        if paragraphs:
            return paragraphs

        chunk_size = 1200
        return [
            text[index : index + chunk_size]
            for index in range(0, len(text), chunk_size)
            if text[index : index + chunk_size].strip()
        ]

    def _keywords_for(self, data: CategoryDetectionPromptData) -> tuple[str, ...]:
        declared = data.declared_category.strip().lower()
        common = ("categoría", "categorias", "años", str(data.age))
        if "aficionado" in declared:
            return common + ("aficionados", "novatos", "promocional")
        if "cicloturista" in declared:
            return common + ("cicloturista", "damas", "varones")
        return common + ("federados", "sub", "elite", "master", "cadetes", "junior")

    def _score_chunk(self, chunk: str, keywords: tuple[str, ...]) -> int:
        normalized = chunk.lower()
        return sum(1 for keyword in keywords if keyword in normalized)

    def _detect_with_mock(self, data: CategoryDetectionPromptData) -> str:
        declared = data.declared_category.strip().lower()
        if "cicloturista" in declared:
            return "Cicloturista"
        if "aficionado" in declared:
            if data.age <= 29:
                return "Aficionados o Novatos 1"
            if data.age <= 39:
                return "Aficionados o Novatos 2"
            if data.age <= 49:
                return "Aficionados o Novatos 3"
            return "Aficionados o Novatos 4"
        if data.age <= 14:
            return "Sub 15"
        if data.age <= 16:
            return "Cadetes"
        if data.age <= 18:
            return "Junior"
        if data.age <= 22:
            return "Sub 23"
        if data.age <= 29:
            return "Elite"
        if data.age <= 35:
            return "Master A1"
        if data.age <= 39:
            return "Master A2"
        if data.age <= 45:
            return "Master B1"
        if data.age <= 49:
            return "Master B2"
        if data.age <= 55:
            return "Master C1"
        if data.age <= 59:
            return "Master C2"
        if data.age <= 65:
            return "Master D1"
        return "Master D2"
