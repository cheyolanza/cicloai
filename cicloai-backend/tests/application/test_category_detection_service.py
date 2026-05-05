from __future__ import annotations

from datetime import date
from unittest.mock import Mock

import pytest

from cicloai.application.category_detection_service import (
    NO_DETERMINADA,
    CategoryDetectionService,
)
from cicloai.rag.category_rules_rag_service import CategoryDetectionPromptData


def build_service(response: str | None):
    rag = Mock()
    rag.detect_category.return_value = response
    return CategoryDetectionService(rag), rag


def test_detect_category_builds_prompt_and_cleans_allowed_response() -> None:
    service, rag = build_service(" Federados  Master A2 ")

    result = service.detect_category(
        birth_date=date(1990, 5, 10),
        declared_category=" FEDERADO ",
        gender=" Masculino ",
        date_of_race=date(2026, 4, 26),
    )

    assert result == "Federado Master A2"
    prompt = rag.detect_category.call_args.args[0]
    assert isinstance(prompt, CategoryDetectionPromptData)
    assert prompt.age == 35
    assert prompt.declared_category == "FEDERADO"
    assert prompt.gender == "Masculino"


def test_detect_category_returns_no_determinada_for_future_birth_date() -> None:
    service, rag = build_service("Sub 15")

    result = service.detect_category(
        birth_date=date(2027, 1, 1),
        declared_category="Federado",
        date_of_race=date(2026, 4, 26),
    )

    assert result == NO_DETERMINADA
    rag.detect_category.assert_not_called()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Sub 15 (Varones y Damas): 13-14 años", "Sub 15"),
        ("Aficionados o Novatos 4 (Varones): 50 años y más", "Aficionados o Novatos 4"),
        ("Cicloturista Damas: 18 años en adelante", "Cicloturista Damas"),
    ],
)
def test_detect_category_accepts_full_convocatoria_labels(
    raw: str, expected: str
) -> None:
    service, _rag = build_service(raw)

    assert (
        service.detect_category(
            birth_date=date(1980, 1, 1),
            declared_category="Aficionado",
            date_of_race=date(2026, 4, 26),
        )
        == expected
    )


@pytest.mark.parametrize(
    "raw",
    [
        None,
        "",
        "Categoria inventada",
        "La categoría detectada es: Master A1",
        "Master A1 porque tiene 36 años",
        "Master A1: Varones",
        "respuesta demasiado larga para ser una categoria",
    ],
)
def test_detect_category_rejects_empty_invalid_or_explanatory_answers(
    raw: str | None,
) -> None:
    service, _rag = build_service(raw)

    assert (
        service.detect_category(
            birth_date=date(1990, 1, 1),
            declared_category="Federado",
            date_of_race=date(2026, 4, 26),
        )
        == NO_DETERMINADA
    )
