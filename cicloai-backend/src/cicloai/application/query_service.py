from __future__ import annotations

from time import perf_counter

from cicloai.domain.entities import RAGAnswer
from cicloai.domain.ports import LLMClient, VectorIndex


class QueryService:
    def __init__(self, vector_index: VectorIndex, llm_client: LLMClient, default_top_k: int = 3) -> None:
        self.vector_index = vector_index
        self.llm_client = llm_client
        self.default_top_k = default_top_k

    def query(self, question: str, top_k: int | None = None) -> RAGAnswer:
        clean_question = question.strip()
        if not clean_question:
            raise ValueError("question is required")

        started_at = perf_counter()
        resolved_top_k = top_k or self.default_top_k
        contexts = self.vector_index.search(clean_question, top_k=resolved_top_k)
        answer = self.llm_client.generate(clean_question, contexts)
        latency_ms = (perf_counter() - started_at) * 1000

        return RAGAnswer(
            answer=answer,
            sources=contexts,
            model=self.llm_client.model_name,
            latency_ms=round(latency_ms, 2),
        )

