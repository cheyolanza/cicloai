from datetime import date
from unittest.mock import Mock

import pytest

from cicloai.application.category_detection_service import (
    ALLOWED_DETECTED_CATEGORIES,
    NO_DETERMINADA,
    CategoryDetectionService,
)
from cicloai.rag.category_rules_rag_service import CategoryDetectionPromptData


def build_service(rag_response: str | None = "Master A1") -> tuple[CategoryDetectionService, Mock]:
    rag_mock = Mock()
    rag_mock.detect_category.return_value = rag_response
    return CategoryDetectionService(rag_service=rag_mock), rag_mock


def test_detect_category_builds_expected_prompt_data() -> None:
    service, rag_mock = build_service("Master A1")

    result = service.detect_category(
        birth_date=date(1990, 1, 10),
        declared_category="  FEDERADO  ",
        gender="  Femenino ",
        date_of_race=date(2026, 4, 26),
    )

    assert result == "Master A1"
    rag_mock.detect_category.assert_called_once()
    prompt_data = rag_mock.detect_category.call_args.args[0]
    assert isinstance(prompt_data, CategoryDetectionPromptData)
    assert prompt_data.birth_date == "1990-01-10"
    assert prompt_data.age == 36
    assert prompt_data.declared_category == "FEDERADO"
    assert prompt_data.gender == "Femenino"
    assert prompt_data.date_of_race == "2026-04-26"


def test_detect_category_uses_today_when_race_date_is_missing() -> None:
    service, rag_mock = build_service("Master A2")

    result = service.detect_category(
        birth_date=date(1990, 1, 1),
        declared_category="FEDERADO",
        gender="Masculino",
        date_of_race=None,
    )

    assert result == "Master A2"
    prompt_data = rag_mock.detect_category.call_args.args[0]
    assert prompt_data.date_of_race == date.today().isoformat()
    assert prompt_data.gender == "Masculino"


def test_detect_category_returns_no_determinada_for_future_birth_date() -> None:
    service, rag_mock = build_service("Master A1")

    result = service.detect_category(
        birth_date=date(2027, 1, 1),
        declared_category="FEDERADO",
        date_of_race=date(2026, 4, 26),
    )

    assert result == NO_DETERMINADA
    rag_mock.detect_category.assert_not_called()


@pytest.mark.parametrize(
    ("raw_response", "expected"),
    [
        ("Master A1", "Master A1"),
        ("   Master   A2   ", "Master A2"),
        ("Cicloturista Damas", "Cicloturista Damas"),
        ("Aficionados o Novatos 2", "Aficionados o Novatos 2"),
    ],
)
def test_detect_category_accepts_allowed_categories(raw_response: str, expected: str) -> None:
    service, _rag_mock = build_service(raw_response)

    result = service.detect_category(
        birth_date=date(1992, 5, 10),
        declared_category="FEDERADO",
        gender="Femenino",
        date_of_race=date(2026, 4, 26),
    )

    assert result == expected


def test_detect_category_normalizes_federado_prefixed_response() -> None:
    service, _rag_mock = build_service("Federados Master A2")

    result = service.detect_category(
        birth_date=date(1990, 1, 10),
        declared_category="FEDERADO",
        gender="Varones",
        date_of_race=date(2026, 4, 26),
    )

    assert result == "Federado Master A2"


@pytest.mark.parametrize(
    ("raw_response", "expected"),
    [
        ("Sub 15 (Varones y Damas): 13-14 años", "Sub 15"),
        ("Cadetes (Varones y Damas): 15-16 años", "Cadetes"),
        ("Junior (Varones y Damas): 17-18 años", "Junior"),
        ("Sub 23 (Varones): 19-22 años", "Sub 23"),
        ("Elite (Varones y Damas): 23-29 años", "Elite"),
        ("Federados Master A1 (Varones y Damas): 30-34 años", "Federado Master A1"),
        ("Federados Master A2 (Varones y Damas): 35-39 años", "Federado Master A2"),
        ("Federados Master B1 (Varones y Damas): 40-44 años", "Federado Master B1"),
        ("Federados Master B2 (Varones y Damas): 45-49 años", "Federado Master B2"),
        ("Federados Master C1 (Varones): 50-54 años", "Federado Master C1"),
        ("Federados Master C2 (Varones): 55-59 años", "Federado Master C2"),
        ("Federados Master C (Damas): 50 años y más", "Federado Master C"),
        ("Federados Master D1 (Varones): 60-64 años", "Federado Master D1"),
        ("Federados Master D2 (Varones): 65-69 años", "Federado Master D2"),
        ("Aficionados o Novatos 1 (Varones y Damas): 16-29 años", "Aficionados o Novatos 1"),
        ("Aficionados o Novatos 2 (Varones y Damas): 30-39 años", "Aficionados o Novatos 2"),
        ("Aficionados o Novatos 3 (Varones y Damas)", "Aficionados o Novatos 3"),
        ("Aficionados o Novatos 3 (Varones y Damas): 40-49 años", "Aficionados o Novatos 3"),
        ("Aficionados o Novatos 4 (Varones): 50 años y más", "Aficionados o Novatos 4"),
        ("Cicloturista Varones: 18 años en adelante", "Cicloturista Varones"),
        ("Cicloturista Damas: 18 años en adelante", "Cicloturista Damas"),
    ],
)
def test_detect_category_accepts_convocatoria_full_labels(raw_response: str, expected: str) -> None:
    service, _rag_mock = build_service(raw_response)

    result = service.detect_category(
        birth_date=date(1980, 5, 10),
        declared_category="AFICIONADO",
        gender="Masculino",
        date_of_race=date(2026, 4, 26),
    )

    assert result == expected


@pytest.mark.parametrize(
    "raw_response",
    [
        None,
        "",
        "Categoria inventada",
        "La categoría detectada es: Master A1",
        "Master A1 porque tiene 36 años",
        "Master A1: Varones",
        "No tengo información sobre eso.",
        "texto demasiado largo para ser solo una categoría válida",
    ],
)
def test_detect_category_rejects_invalid_or_explanatory_answers(raw_response: str | None) -> None:
    service, _rag_mock = build_service(raw_response)

    result = service.detect_category(
        birth_date=date(1992, 5, 10),
        declared_category="FEDERADO",
        gender="Varones",
        date_of_race=date(2026, 4, 26),
    )

    assert result == NO_DETERMINADA


@pytest.mark.parametrize("category", sorted(ALLOWED_DETECTED_CATEGORIES))
def test_clean_category_keeps_allowed_categories(category: str) -> None:
    service, _rag_mock = build_service(category)

    assert service.detect_category(
        birth_date=date(1992, 5, 10),
        declared_category="FEDERADO",
        date_of_race=date(2026, 4, 26),
    ) == category


def test_clean_category_rejects_categories_not_in_allow_list() -> None:
    service, _rag_mock = build_service("Master Z9")

    assert service.detect_category(
        birth_date=date(1992, 5, 10),
        declared_category="FEDERADO",
        date_of_race=date(2026, 4, 26),
    ) == NO_DETERMINADA
