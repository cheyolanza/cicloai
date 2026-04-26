from __future__ import annotations

import httpx

from cicloai.infrastructure.config import Settings


class CaptchaService:
    """Validates frontend CAPTCHA tokens and supports a local mock token."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def verify(self, captcha_token: str) -> bool:
        if self._settings.enable_captcha_mock:
            return captcha_token == "mock-valid-captcha"

        if not self._settings.google_recaptcha_secret_key:
            return False

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": self._settings.google_recaptcha_secret_key,
                    "response": captcha_token,
                },
            )
            response.raise_for_status()

        return bool(response.json().get("success"))
