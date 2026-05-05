from unittest.mock import Mock

from cicloai.application.payment_validation_service import PaymentValidationService


def test_extract_payment_data_from_qr_ocr_text():
    service = PaymentValidationService(Mock())

    result = service.extract_payment_data(
        """
        Banco Union
        Comprobante de pago QR
        Monto: Bs. 60.00
        Fecha: 2026-04-25
        ID Transaccion: ABC-123456
        """
    )

    assert str(result.amount) == "60.00"
    assert result.id_transaction == "ABC-123456"
    assert result.payment_date.isoformat() == "2026-04-25"
    assert result.bank_name == "BANCO UNION"


def test_extract_payment_data_from_spanish_text_date_and_nro_transaction():
    service = PaymentValidationService(Mock())

    result = service.extract_payment_data(
        """
        Banco Union
        Monto Bs. 60
        Fecha 21 de Abril, 2026
        Nro. 1234567890
        """
    )

    assert str(result.amount) == "60.00"
    assert result.id_transaction == "1234567890"
    assert result.payment_date.isoformat() == "2026-04-21"
    assert result.bank_name == "BANCO UNION"


def test_extract_payment_data_returns_none_for_missing_required_values():
    service = PaymentValidationService(Mock())

    result = service.extract_payment_data(
        "Comprobante borroso sin valores estructurados"
    )

    assert result.amount is None
    assert result.id_transaction is None
    assert result.payment_date is None
    assert result.bank_name is None
