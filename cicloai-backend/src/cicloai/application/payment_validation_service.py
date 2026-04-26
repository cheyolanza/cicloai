from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from cicloai.application.payment_proof_ocr_service import PaymentOcrResult
from cicloai.infrastructure.models.bike_race import BikeRace
from cicloai.infrastructure.models.race_qr_payment import RaceQrPayment

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PaymentDataExtraction:
    """Structured values parsed from OCR text before business validation."""

    amount: Decimal | None
    id_transaction: str | None
    payment_date: date | None
    bank_name: str | None


@dataclass(frozen=True)
class PaymentValidationResult:
    """Business validation result persisted for the review/confirmation flow."""

    payment_id: UUID
    status: str
    reference: str
    message: str
    provider: str
    extracted_text: str | None
    extracted_amount: Decimal | None
    expected_amount: Decimal
    currency: str
    id_transaction: str | None
    payment_date: date | None
    bank_name: str | None

    @property
    def is_valid(self) -> bool:
        return self.status == "validated"


class PaymentValidationService:
    """Validates QR payment proofs using OCR text plus race payment rules.

    OCR remains an adapter concern; this service owns CicloAI business rules:
    amount equality, payment date freshness and transaction-id uniqueness. The
    same contract can be reused later for bulk payments or existing-user flows.
    """

    _BANK_ALIASES = (
        "BANCO UNION",
        "BANCO UNIÓN",
        "BNB",
        "BANCO NACIONAL",
        "BANCO MERCANTIL",
        "MERCANTIL SANTA CRUZ",
        "BANCO BISA",
        "BISA",
        "BANCO GANADERO",
        "GANADERO",
        "BANCO ECONOMICO",
        "BANCO ECONÓMICO",
    )

    def __init__(self, db: Session) -> None:
        self._db = db

    def validate_payment_proof(
        self,
        *,
        race: BikeRace,
        ocr_result: PaymentOcrResult,
        proof_path: Path,
        expected_amount: Decimal,
        current_date: date | None = None,
    ) -> PaymentValidationResult:
        today = current_date or date.today()
        self._log_ocr_input(
            proof_path=proof_path,
            ocr_result=ocr_result,
            race=race,
            expected_amount=expected_amount,
        )
        extracted = self.extract_payment_data(ocr_result.extracted_text or "")
        status, message = self._validate_extracted_data(
            extracted=extracted,
            expected_amount=expected_amount,
            currency=race.currency,
            today=today,
            ocr_result=ocr_result,
        )

        id_transaction = extracted.id_transaction
        if status == "validated" and id_transaction and self._transaction_exists(id_transaction):
            status = "rejected"
            message = "El id de transacción ya fue registrado previamente."

        self._log_payment_validation(
            extracted=extracted,
            status=status,
            message=message,
            expected_amount=expected_amount,
            currency=race.currency,
        )

        payment = RaceQrPayment(
            bike_race_id=race.id,
            expected_amount=expected_amount,
            extracted_amount=extracted.amount,
            currency=race.currency,
            id_transaction=id_transaction if status == "validated" else None,
            payment_date=extracted.payment_date,
            bank_name=extracted.bank_name,
            proof_file_path=str(proof_path),
            ocr_provider=ocr_result.provider,
            ocr_text=ocr_result.extracted_text,
            status=status,
            rejection_reason=None if status == "validated" else message,
        )
        self._db.add(payment)
        self._db.flush()

        return PaymentValidationResult(
            payment_id=payment.id,
            status=status,
            reference=id_transaction or ocr_result.reference,
            message=message,
            provider=ocr_result.provider,
            extracted_text=ocr_result.extracted_text,
            extracted_amount=extracted.amount,
            expected_amount=expected_amount,
            currency=race.currency,
            id_transaction=id_transaction,
            payment_date=extracted.payment_date,
            bank_name=extracted.bank_name,
        )

    def _log_ocr_input(
        self,
        *,
        proof_path: Path,
        ocr_result: PaymentOcrResult,
        race: BikeRace,
        expected_amount: Decimal,
    ) -> None:
        """Logs OCR input metadata without exposing credentials or binary data."""

        file_size = proof_path.stat().st_size if proof_path.exists() else 0
        logger.info(
            "payment_ocr_input proof_file=%s file_size_bytes=%s suffix=%s provider=%s ocr_valid=%s race_id=%s expected_amount=%s currency=%s text_length=%s",
            proof_path.name,
            file_size,
            proof_path.suffix.lower(),
            ocr_result.provider,
            ocr_result.is_valid,
            race.id,
            expected_amount,
            race.currency,
            len(ocr_result.extracted_text or ""),
        )

    def _log_payment_validation(
        self,
        *,
        extracted: PaymentDataExtraction,
        status: str,
        message: str,
        expected_amount: Decimal,
        currency: str,
    ) -> None:
        """Logs the parsed OCR payment fields and final validation decision."""

        logger.info(
            "payment_ocr_detected amount=%s expected_amount=%s currency=%s payment_date=%s id_transaction=%s bank_name=%s payment_valid=%s status=%s message=%s",
            extracted.amount,
            expected_amount,
            currency,
            extracted.payment_date,
            extracted.id_transaction,
            extracted.bank_name,
            status == "validated",
            status,
            message,
        )

    def attach_to_biker(self, payment_id: UUID, competition_biker_id: UUID) -> None:
        payment = self._db.get(RaceQrPayment, payment_id)
        if payment is None:
            raise ValueError("No se encontró la validación de pago asociada a esta inscripción.")
        if payment.status != "validated":
            raise ValueError("El pago asociado no está validado.")

        payment.competition_biker_id = competition_biker_id

    def extract_payment_data(self, text: str) -> PaymentDataExtraction:
        normalized = self._normalize_text(text)
        return PaymentDataExtraction(
            amount=self._extract_amount(normalized),
            id_transaction=self._extract_transaction_id(normalized),
            payment_date=self._extract_date(normalized),
            bank_name=self._extract_bank_name(normalized),
        )

    def _validate_extracted_data(
        self,
        *,
        extracted: PaymentDataExtraction,
        expected_amount: Decimal,
        currency: str,
        today: date,
        ocr_result: PaymentOcrResult,
    ) -> tuple[str, str]:
        if not ocr_result.is_valid:
            return "rejected", ocr_result.message
        if extracted.amount is None:
            return "rejected", "No se pudo identificar el monto del comprobante."
        if extracted.amount != expected_amount:
            return (
                "rejected",
                f"El monto del comprobante ({extracted.amount} {currency}) no coincide con el monto esperado ({expected_amount} {currency}).",
            )
        if not extracted.id_transaction:
            return "rejected", "No se pudo identificar el id de transacción del comprobante."
        if not extracted.bank_name:
            return "rejected", "No se pudo identificar el banco del comprobante."
        if extracted.payment_date is None:
            return "rejected", "No se pudo identificar una fecha válida en el comprobante."
        if extracted.payment_date != today:
            return "rejected", "La fecha del comprobante no corresponde al día de hoy."

        return "validated", "Pago validado correctamente: monto, fecha e id de transacción coinciden."

    def _transaction_exists(self, id_transaction: str) -> bool:
        statement = select(RaceQrPayment.id).where(RaceQrPayment.id_transaction == id_transaction).limit(1)
        return self._db.execute(statement).scalar_one_or_none() is not None

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"[ \t]+", " ", text.upper())

    @staticmethod
    def _extract_amount(text: str) -> Decimal | None:
        amount_keywords = r"(?:MONTO|IMPORTE|TOTAL|PAGADO|PAGO|BS\.?|BOB)"
        pattern = re.compile(rf"{amount_keywords}[^\d]{{0,30}}(\d{{1,5}}(?:[.,]\d{{1,2}})?)")
        for match in pattern.finditer(text):
            amount = PaymentValidationService._to_decimal(match.group(1))
            if amount is not None:
                return amount

        bs_pattern = re.compile(r"(?:BS\.?|BOB)\s*(\d{1,5}(?:[.,]\d{1,2})?)")
        for match in bs_pattern.finditer(text):
            amount = PaymentValidationService._to_decimal(match.group(1))
            if amount is not None:
                return amount
        return None

    @staticmethod
    def _to_decimal(value: str) -> Decimal | None:
        try:
            return Decimal(value.replace(",", ".")).quantize(Decimal("0.01"))
        except InvalidOperation:
            return None

    @staticmethod
    def _extract_transaction_id(text: str) -> str | None:
        patterns = (
            r"\bNRO\.?\s*[:#-]?\s*(\d{10})\b",
            r"(?:ID|NRO|NÚMERO|NUMERO|CODIGO|CÓDIGO|REFERENCIA)[^\n:]{0,35}(?:TRANSACCI[ÓO]N|OPERACI[ÓO]N|COMPROBANTE)?\s*[:#-]\s*([A-Z0-9][A-Z0-9-]{5,})",
            r"(?:TRANSACCI[ÓO]N|OPERACI[ÓO]N|COMPROBANTE)\s*[:#-]\s*([A-Z0-9][A-Z0-9-]{5,})",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip("- ")
        return None

    @staticmethod
    def _extract_date(text: str) -> date | None:
        date_patterns = (
            (r"\b(\d{4}-\d{2}-\d{2})\b", "%Y-%m-%d"),
            (r"\b(\d{2}/\d{2}/\d{4})\b", "%d/%m/%Y"),
            (r"\b(\d{2}-\d{2}-\d{4})\b", "%d-%m-%Y"),
        )
        for pattern, date_format in date_patterns:
            match = re.search(pattern, text)
            if not match:
                continue
            try:
                return datetime.strptime(match.group(1), date_format).date()
            except ValueError:
                continue

        textual_match = re.search(
            r"\b(\d{1,2})\s+DE\s+([A-ZÁÉÍÓÚÑ]+),?\s+(\d{4})\b",
            text,
        )
        if textual_match:
            day_text, month_text, year_text = textual_match.groups()
            month = PaymentValidationService._spanish_month_number(month_text)
            if month is not None:
                try:
                    return date(int(year_text), month, int(day_text))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _spanish_month_number(month_text: str) -> int | None:
        months = {
            "ENERO": 1,
            "FEBRERO": 2,
            "MARZO": 3,
            "ABRIL": 4,
            "MAYO": 5,
            "JUNIO": 6,
            "JULIO": 7,
            "AGOSTO": 8,
            "SEPTIEMBRE": 9,
            "SETIEMBRE": 9,
            "OCTUBRE": 10,
            "NOVIEMBRE": 11,
            "DICIEMBRE": 12,
        }
        return months.get(month_text.strip().upper())

    def _extract_bank_name(self, text: str) -> str | None:
        for bank in self._BANK_ALIASES:
            if bank in text:
                return bank

        match = re.search(r"BANCO\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ ]{3,40})", text)
        if match:
            return f"BANCO {match.group(1).strip()}"
        return None
