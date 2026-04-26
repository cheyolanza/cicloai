from datetime import date
from pathlib import Path
from unittest.mock import Mock

from cicloai.application.registration_service import BulkExcelService, CategoryRulesService


def test_bulk_excel_service_parses_gender_column() -> None:
    service = BulkExcelService()

    competitors = service.parse(
        filename="bulk.csv",
        file_bytes=(
            "DNI,Nombre Completo,Fecha Nacimiento,Genero,Categoria\n"
            "1234567,Juan Perez,1990-01-10,Masculino,Federado\n"
        ).encode("utf-8"),
    )

    assert len(competitors) == 1
    assert competitors[0].gender == "Masculino"
    assert competitors[0].requested_category == "Federado"


def test_category_rules_service_passes_gender_to_detector() -> None:
    detector = Mock()
    detector.detect_category.return_value = "Master A2"
    service = CategoryRulesService(Path("convocatoria.txt"), detector)
    race = Mock(date_of_race=date(2026, 4, 26))

    result = service.validate(
        birth_date=date(1990, 1, 10),
        requested_category="FEDERADO",
        gender="Femenino",
        race=race,
    )

    detector.detect_category.assert_called_once()
    assert detector.detect_category.call_args.kwargs["gender"] == "Femenino"
    assert result.valid is True
    assert result.detected_category == "Master A2"
