from __future__ import annotations

SYSTEM_PROMPT = """Eres CicloAI, un agente especializado en asistir a usuarios sobre la convocatoria de una competencia de ciclismo.

Reglas obligatorias:
1. Responde únicamente con base en el contexto proporcionado.
2. Solo puedes responder preguntas relacionadas con la convocatoria de la carrera.
3. No inventes datos.
4. Si la información no está en el contexto, responde: "No tengo información sobre eso."
5. Si la pregunta no está relacionada con la convocatoria, responde: "No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera."
6. Responde en español.
7. Mantén respuestas claras, breves y útiles.
8. No des asesoría médica, legal o financiera."""


class PromptBuilder:
    def build_messages(
        self, question: str, context_rows: list[dict]
    ) -> list[dict[str, str]]:
        context = "\n\n".join(
            f"[{row['metadata'].get('source_file')}::{row['metadata'].get('chunk_id')}]\n{row['text']}"
            for row in context_rows
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Contexto recuperado:\n{context}\n\nPregunta del usuario:\n{question}",
            },
        ]

    def build_category_detection_messages(
        self,
        *,
        context: str,
        birth_date: str,
        age: int,
        declared_category: str,
        gender: str | None,
        date_of_race: str,
    ) -> list[dict[str, str]]:
        """Builds a strict category-classification prompt.

        This prompt intentionally asks for a single category name and nothing
        else. The application layer still validates the model output against an
        allow-list before accepting it.
        """

        prompt = f"""Eres un motor de clasificación de categorías para una competencia de ciclismo.

Debes determinar la categoría exacta del competidor usando únicamente el CONTEXTO de la convocatoria.

Reglas obligatorias:
1. Responde SOLO con el nombre exacto de la categoría.
2. No expliques.
3. No agregues prefijos.
4. No uses markdown.
5. No inventes categorías.
6. Si no puedes determinar la categoría con el contexto, responde: NO_DETERMINADA.
7. Usa la edad calculada, la fecha de nacimiento, el tipo declarado y el género si está disponible.
8. Si el tipo declarado es Aficionado, usa únicamente categorías Aficionados o Novatos.
9. Si el tipo declarado es Cicloturista, usa únicamente Cicloturista.
10. Si el tipo declarado es Federado, usa categorías oficiales/federadas.

CONTEXTO:
{context}

DATOS DEL COMPETIDOR:
Fecha de nacimiento: {birth_date}
Edad calculada: {age}
Tipo declarado: {declared_category}
Género: {gender or "No disponible"}
Fecha de carrera: {date_of_race}

Responde únicamente con el nombre de la categoría."""

        return [{"role": "user", "content": prompt}]
