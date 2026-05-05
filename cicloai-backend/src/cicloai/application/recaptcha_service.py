from __future__ import annotations

from dataclasses import dataclass, field

from cicloai.infrastructure.config import Settings


@dataclass(frozen=True)
class RecaptchaAssessment:
    valid: bool
    action: str
    score: float | None = None
    reasons: list[str] = field(default_factory=list)


class RecaptchaVerificationService:
    """Validates reCAPTCHA Enterprise tokens behind the API boundary.

    Frontend tokens expire quickly and must never be trusted by the browser
    alone. This service keeps Google Cloud client code isolated so the API can
    run in mock mode locally and switch to real assessments in deployed
    environments with credentials configured.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def verify(self, token: str, expected_action: str) -> RecaptchaAssessment:
        if self._settings.recaptcha_enable_mocks:
            return self._verify_mock(token=token, expected_action=expected_action)

        return self._create_assessment(token=token, expected_action=expected_action)

    def _verify_mock(self, token: str, expected_action: str) -> RecaptchaAssessment:
        valid = bool(token.strip()) and expected_action == "LOGIN"
        return RecaptchaAssessment(
            valid=valid,
            action=expected_action,
            score=0.9 if valid else 0.0,
            reasons=[] if valid else ["MOCK_INVALID_TOKEN_OR_ACTION"],
        )

    def _create_assessment(
        self, token: str, expected_action: str
    ) -> RecaptchaAssessment:
        try:
            from google.cloud import recaptchaenterprise_v1
        except ImportError as exc:
            raise RuntimeError(
                "google-cloud-recaptcha-enterprise is required when RECAPTCHA_ENABLE_MOCKS=false"
            ) from exc

        client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()
        project_path = f"projects/{self._settings.recaptcha_project_id}"
        event = recaptchaenterprise_v1.Event(
            token=token, site_key=self._settings.recaptcha_site_key
        )
        assessment = recaptchaenterprise_v1.Assessment(event=event)
        request = recaptchaenterprise_v1.CreateAssessmentRequest(
            parent=project_path, assessment=assessment
        )
        response = client.create_assessment(request=request)

        token_properties = response.token_properties
        if not token_properties.valid:
            return RecaptchaAssessment(
                valid=False,
                action=token_properties.action,
                score=None,
                reasons=[str(token_properties.invalid_reason)],
            )

        score = response.risk_analysis.score
        reasons = [str(reason) for reason in response.risk_analysis.reasons]
        valid = (
            token_properties.action == expected_action
            and score >= self._settings.recaptcha_min_score
        )

        if token_properties.action != expected_action:
            reasons.append("ACTION_MISMATCH")

        if score < self._settings.recaptcha_min_score:
            reasons.append("LOW_SCORE")

        return RecaptchaAssessment(
            valid=valid, action=token_properties.action, score=score, reasons=reasons
        )
