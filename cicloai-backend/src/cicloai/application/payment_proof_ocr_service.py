from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from cicloai.application.google_vision_ocr_service import GoogleVisionOcrService
from cicloai.infrastructure.config import Settings


@dataclass(frozen=True)
class PaymentOcrResult:
    is_valid: bool
    provider: str
    extracted_text: str | None
    confidence: float | None
    message: str

    @property
    def status(self) -> str:
        return "ocr_validated" if self.is_valid else "ocr_rejected"

    @property
    def reference(self) -> str:
        if self.provider == "mock":
            return "OCR-MOCK"
        return "GOOGLE-VISION-OCR"


class PaymentProofOcrService:
    """Reusable OCR facade for all payment-proof flows.

    The registration use cases depend on this facade instead of Google Vision
    directly. Local development can keep `ENABLE_OCR_MOCK=true`, while
    production routes the same uploaded file through Google Vision using a
    service-account JSON mounted into the container.
    """

    _SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(
        self, settings: Settings, google_vision: GoogleVisionOcrService | None = None
    ) -> None:
        self._settings = settings
        self._google_vision = google_vision or GoogleVisionOcrService(settings)

    def analyze_payment_proof(self, image_path: Path) -> PaymentOcrResult:
        suffix = image_path.suffix.lower()
        if suffix not in self._SUPPORTED_EXTENSIONS:
            raise ValueError("Formato de archivo no soportado para OCR.")

        if self._settings.enable_ocr_mock:
            return self._analyze_with_mock(image_path)

        extracted_text = self._google_vision.extract_text(image_path)
        if not extracted_text:
            return PaymentOcrResult(
                is_valid=False,
                provider="google_vision",
                extracted_text=None,
                confidence=None,
                message="No se encontró texto en el comprobante.",
            )

        return PaymentOcrResult(
            is_valid=True,
            provider="google_vision",
            extracted_text=extracted_text,
            confidence=None,
            message="Comprobante procesado correctamente con Google Vision OCR",
        )

    def _analyze_with_mock(self, image_path: Path) -> PaymentOcrResult:
        if not image_path.exists() or image_path.stat().st_size == 0:
            return PaymentOcrResult(
                is_valid=False,
                provider="mock",
                extracted_text=None,
                confidence=None,
                message="El comprobante debe ser una imagen válida.",
            )

        return PaymentOcrResult(
            is_valid=True,
            provider="mock",
            extracted_text=(
                "BANCO UNION\n"
                "Comprobante de pago QR\n"
                "Monto: Bs. 60.00\n"
                f"Fecha: {date.today().isoformat()}\n"
                f"ID Transaccion: MOCK-{image_path.stem.upper()}"
            ),
            confidence=1.0,
            message="Comprobante legible según validación OCR mock.",
        )
