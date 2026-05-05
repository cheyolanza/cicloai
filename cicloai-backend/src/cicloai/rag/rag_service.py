from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from cicloai.rag.config import RagConfig
from cicloai.rag.prompt_builder import PromptBuilder
from cicloai.rag.retriever import Retriever


OUT_OF_DOMAIN_MESSAGE = "No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera."
NO_CONTEXT_MESSAGE = "No tengo información sobre eso."


@dataclass(frozen=True)
class RagSource:
    source_file: str
    chunk_id: str | None = None


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[RagSource]


class RagService:
    """Orchestrates retrieval, guarded prompting and OpenAI completion."""

    def __init__(
        self, config: RagConfig, retriever: Retriever, prompt_builder: PromptBuilder
    ) -> None:
        self._config = config
        self._retriever = retriever
        self._prompt_builder = prompt_builder
        self._openai = OpenAI(api_key=config.openai_api_key)

    def answer(self, question: str) -> RagAnswer:
        if not self.is_convocatoria_domain(question):
            return RagAnswer(answer=OUT_OF_DOMAIN_MESSAGE, sources=[])

        context_rows = self._retriever.retrieve(question)
        if not context_rows:
            return RagAnswer(answer=NO_CONTEXT_MESSAGE, sources=[])

        messages = self._prompt_builder.build_messages(question, context_rows)
        response = self._openai.chat.completions.create(
            model=self._config.chat_model,
            messages=messages,
            temperature=0,
        )
        answer = response.choices[0].message.content or NO_CONTEXT_MESSAGE
        return RagAnswer(
            answer=answer,
            sources=[
                RagSource(
                    source_file=row["metadata"].get("source_file", ""),
                    chunk_id=row["metadata"].get("chunk_id"),
                )
                for row in context_rows
            ],
        )

    @staticmethod
    def is_convocatoria_domain(question: str) -> bool:
        """Cheap domain gate used before invoking embeddings or the LLM."""
        normalized = question.lower()
        keywords = (
            "convocatoria",
            "lugar",
            "fecha",
            "hora",
            "categoria",
            "categoría",
            "edad",
            "modalidad",
            "distancia",
            "inscripcion",
            "inscripción",
            "costo",
            "regla",
            "uniforme",
            "premiacion",
            "premiación",
            "seguridad",
            "requisito",
            "participacion",
            "participación",
            "dorsal",
            "carrera",
            "ubicacion",
            "ubicación",
            "recojo",
            "participante",
            "participantes",
            "mínimo",
            "minimo",
            "mínima",
            "minima",
            "club",
            "clubes",
            "control",
            "accidente",
            "accidentes",
            "bioseguridad",
            "casco",
            "audífonos",
            "audifonos",
            "parlantes",
        )
        return any(keyword in normalized for keyword in keywords)
