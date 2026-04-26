from __future__ import annotations

from datetime import date

from cicloai.rag.category_rules_rag_service import CategoryDetectionPromptData, CategoryRulesRagService


NO_DETERMINADA = "NO_DETERMINADA"

BASE_DETECTED_CATEGORIES = {
    "Sub 15",
    "Cadetes",
    "Junior",
    "Sub 23",
    "Elite",
    "Master A1",
    "Master A2",
    "Master B1",
    "Master B2",
    "Master C1",
    "Master C2",
    "Master C",
    "Master D1",
    "Master D2",
    "Aficionados o Novatos 1",
    "Aficionados o Novatos 2",
    "Aficionados o Novatos 3",
    "Aficionados o Novatos 4",
    "Cicloturista",
    "Cicloturista Varones",
    "Cicloturista Damas",
}

FEDERATED_DETECTED_CATEGORIES = {f"Federado {category}" for category in BASE_DETECTED_CATEGORIES if category.startswith("Master ")}
FEDERATED_DETECTED_CATEGORIES.update(
    {
        "Federado Sub 15",
        "Federado Cadetes",
        "Federado Junior",
        "Federado Sub 23",
        "Federado Elite",
    }
)

ALLOWED_DETECTED_CATEGORIES = BASE_DETECTED_CATEGORIES | FEDERATED_DETECTED_CATEGORIES


class CategoryDetectionService:
    """Determines a biker category through the convocatoria RAG service.

    This service owns deterministic parts of the decision: age calculation,
    prompt input normalization and strict LLM-response validation. The RAG
    adapter only returns text; the application accepts it only when it is a
    clean category from the allow-list.
    """

    def __init__(self, rag_service: CategoryRulesRagService) -> None:
        self._rag_service = rag_service

    def detect_category(
        self,
        *,
        birth_date: date,
        declared_category: str,
        gender: str | None = None,
        date_of_race: date | None = None,
    ) -> str:
        reference_date = date_of_race or date.today()
        age = self._calculate_age(birth_date=birth_date, reference_date=reference_date)
        if age < 0:
            return NO_DETERMINADA
        
        print(
            "[CicloAI][CategoryDetectionService.detectCategory] detector_input="
            f"{{birth_date={birth_date.isoformat()}, requested_category={declared_category}, "
            f"gender={gender}, race_date={reference_date if reference_date else None}}}",
            f"age={age}",
            flush=True,
        )

        raw_category = self._rag_service.detect_category(
            CategoryDetectionPromptData(
                birth_date=birth_date.isoformat(),
                age=age,
                declared_category=declared_category.strip(),
                gender=gender.strip() if gender else None,
                date_of_race=reference_date.isoformat(),
            )
        )
        print( f"raw_category={raw_category}", flush=True )
        return self._clean_category(raw_category)

    def _calculate_age(self, *, birth_date: date, reference_date: date) -> int:
        years = reference_date.year - birth_date.year
        has_not_had_birthday = (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day)
        return years - 1 if has_not_had_birthday else years

    def _clean_category(self, response: str | None) -> str:
        if not response:
            return NO_DETERMINADA

        candidate = " ".join(response.strip().split())
        lowered_candidate = candidate.lower()
        if lowered_candidate.startswith("federado ") or lowered_candidate.startswith("federados "):
            parts = candidate.split(maxsplit=1)
            candidate = f"Federado {parts[1]}" if len(parts) > 1 else "Federado"

        lowered = candidate.lower()
        invalid_fragments = (
            ":",
            "la categoría",
            "categoria detectada",
            "categoría detectada",
            "según",
            "porque",
            "pertenece",
        )
        if any(fragment in lowered for fragment in invalid_fragments):
            return NO_DETERMINADA

        if len(candidate.split()) > 5:
            return NO_DETERMINADA

        return candidate if candidate in ALLOWED_DETECTED_CATEGORIES else NO_DETERMINADA
