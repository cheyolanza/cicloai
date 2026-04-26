from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any

import google.auth
import google.auth.transport.requests
import requests

from cicloai.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class GoogleVisionOcrConfigurationError(RuntimeError):
    """Raised when Google Vision credentials are missing or unusable."""


class GoogleVisionOcrProcessingError(RuntimeError):
    """Raised when Google Vision cannot process the requested image."""


class GoogleVisionOcrService:
    """Thin Google Vision API adapter for text extraction from payment proofs.

    Authentication is delegated to `google.auth.default`, which reads the
    service-account JSON from `GOOGLE_APPLICATION_CREDENTIALS`. Keeping this as
    an adapter makes the payment flow independent from Google-specific HTTP and
    leaves room to add AWS Textract or another provider behind the same
    orchestration service later.
    """

    _SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    def __init__(self, settings: Settings, timeout_seconds: int = 30) -> None:
        self._settings = settings
        self._timeout_seconds = timeout_seconds

    def extract_text(self, image_path: Path) -> str:
        if not image_path.exists() or not image_path.is_file():
            raise GoogleVisionOcrProcessingError("El archivo del comprobante no existe.")

        credentials_path = self._settings.google_application_credentials
        if not credentials_path or not Path(credentials_path).exists():
            raise GoogleVisionOcrConfigurationError(
                "Google OCR no está configurado correctamente. Verifique GOOGLE_APPLICATION_CREDENTIALS."
            )

        access_token = self._get_access_token()
        payload = self._build_payload(image_path)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            response = requests.post(
                self._settings.google_vision_ocr_endpoint,
                json=payload,
                headers=headers,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Google Vision OCR request failed: %s", exc.__class__.__name__)
            raise GoogleVisionOcrProcessingError(
                "No se pudo procesar el comprobante con Google Vision OCR."
            ) from exc

        return self._extract_full_text(response.json())

    def _get_access_token(self) -> str:
        try:
            credentials, _project_id = google.auth.default(scopes=list(self._SCOPES))
            credentials.refresh(google.auth.transport.requests.Request())
        except Exception as exc:
            logger.warning("Google Vision OCR credentials failed: %s", exc.__class__.__name__)
            raise GoogleVisionOcrConfigurationError(
                "Google OCR no está configurado correctamente. Verifique GOOGLE_APPLICATION_CREDENTIALS."
            ) from exc

        token = getattr(credentials, "token", None)
        if not token:
            raise GoogleVisionOcrConfigurationError(
                "Google OCR no está configurado correctamente. Verifique GOOGLE_APPLICATION_CREDENTIALS."
            )
        return str(token)

    def _build_payload(self, image_path: Path) -> dict[str, Any]:
        encoded_image = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        return {
            "requests": [
                {
                    "image": {"content": encoded_image},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }

    def _extract_full_text(self, response_payload: dict[str, Any]) -> str:
        responses = response_payload.get("responses")
        if not isinstance(responses, list) or not responses:
            return ""

        first_response = responses[0]
        if not isinstance(first_response, dict):
            return ""

        if "error" in first_response:
            logger.warning("Google Vision OCR returned an error response.")
            raise GoogleVisionOcrProcessingError("No se pudo procesar el comprobante con Google Vision OCR.")

        annotation = first_response.get("fullTextAnnotation")
        if not isinstance(annotation, dict):
            return ""

        text = annotation.get("text")
        return text.strip() if isinstance(text, str) else ""
