import { useState, type MouseEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAccessSession } from '@/features/access/context/AccessSessionContext';
import { captchaService } from '@/features/access/services/captchaService';

/**
 * Orchestrates the access gate: validate human challenge, mint a temporary
 * token and move the user to the agent. Keeping this orchestration in a hook
 * prevents token/captcha details from spreading across presentational code.
 */
export function useHumanValidation() {
  const navigate = useNavigate();
  const { createTemporarySession } = useAccessSession();
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function validate(event?: MouseEvent<HTMLButtonElement>): Promise<void> {
    event?.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = recaptchaToken ?? captchaService.getWidgetToken();

      if (!token) {
        setError('Completa la validación reCAPTCHA antes de continuar.');
        setLoading(false);
        return;
      }

      const result = await captchaService.validate(token, 'LOGIN');

      if (!result.valid) {
        setError('No pudimos completar la validación humana. Intenta nuevamente.');
        setLoading(false);
        return;
      }

      createTemporarySession(result.accessToken);
      navigate('/agent', { replace: true });
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : 'Error inesperado al validar reCAPTCHA.');
      setLoading(false);
    }
  }

  return { recaptchaToken, setRecaptchaToken, loading, error, validate };
}
