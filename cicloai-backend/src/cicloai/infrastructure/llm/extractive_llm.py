from __future__ import annotations

from cicloai.application.chunking import tokenize
from cicloai.domain.entities import RetrievedChunk


class ExtractiveLLMClient:
    model_name = "local-extractive-rag"

    def generate(self, query: str, contexts: list[RetrievedChunk]) -> str:
        if not contexts:
            return (
                "No tengo informacion suficiente en la base de conocimiento de CicloAI "
                "para responder esa consulta."
            )

        query_terms = set(tokenize(query))
        best_sentences: list[str] = []

        for context in contexts:
            sentences = self._split_sentences(context.chunk.text)
            best_sentence = max(
                sentences,
                key=lambda sentence: len(query_terms.intersection(tokenize(sentence))),
                default=context.chunk.text,
            )
            if best_sentence and best_sentence not in best_sentences:
                best_sentences.append(best_sentence)

        answer = " ".join(best_sentences[:3]).strip()
        if not answer:
            answer = contexts[0].chunk.text

        return f"Segun la base de conocimiento de CicloAI: {answer}"

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        normalized = text.replace("\n", " ").strip()
        if not normalized:
            return []

        separators = [". ", "; ", "\n"]
        sentences = [normalized]
        for separator in separators:
            next_sentences: list[str] = []
            for sentence in sentences:
                next_sentences.extend(
                    part.strip() for part in sentence.split(separator) if part.strip()
                )
            sentences = next_sentences

        return sentences
