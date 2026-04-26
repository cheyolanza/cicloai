import { useEffect, useRef, useState } from 'react';
import { Alert, Box } from '@mui/material';
import { appConfig } from '@/config/env';

interface RecaptchaEnterpriseWidgetProps {
  action: string;
  onTokenChange: (token: string | null) => void;
}

/**
 * reCAPTCHA Enterprise widget integration.
 * The rendered element intentionally keeps `g-recaptcha`, `data-sitekey` and
 * `data-action` so the markup matches Google's widget configuration, while the
 * explicit render call keeps the SPA reliable when the script loads before
 * React mounts this component.
 */
export function RecaptchaEnterpriseWidget({ action, onTokenChange }: RecaptchaEnterpriseWidgetProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const widgetIdRef = useRef<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    window.onCaptchaSuccess = (token: string) => {
      setError(null);
      onTokenChange(token);
    };
    window.onCaptchaExpired = () => {
      onTokenChange(null);
      setError('La validación reCAPTCHA expiró. Vuelve a completarla.');
    };

    function renderWidget(): void {
      const recaptcha = window.grecaptcha?.enterprise;

      if (!recaptcha || !containerRef.current) {
        attempts += 1;

        if (attempts <= 20) {
          window.setTimeout(renderWidget, 150);
          return;
        }

        setError('No se pudo cargar reCAPTCHA Enterprise. Revisa la conexión o la clave del sitio.');
        return;
      }

      if (cancelled || widgetIdRef.current !== null) {
        return;
      }

      recaptcha.ready(() => {
        if (!containerRef.current || cancelled || widgetIdRef.current !== null) {
          return;
        }

        widgetIdRef.current = recaptcha.render(containerRef.current, {
          sitekey: appConfig.recaptchaEnterpriseSiteKey,
          action,
          callback: (token: string) => {
            window.onCaptchaSuccess?.(token);
          },
          'expired-callback': () => {
            window.onCaptchaExpired?.();
          },
          'error-callback': () => {
            onTokenChange(null);
            setError('reCAPTCHA no pudo completar la validación.');
          },
        });
      });
    }

    renderWidget();

    return () => {
      cancelled = true;

      if (widgetIdRef.current !== null) {
        window.grecaptcha?.enterprise.reset(widgetIdRef.current);
      }

      delete window.onCaptchaSuccess;
      delete window.onCaptchaExpired;
    };
  }, [action, onTokenChange]);

  return (
    <Box>
      <Box
        ref={containerRef}
        className="g-recaptcha"
        data-sitekey={appConfig.recaptchaEnterpriseSiteKey}
        data-action={action}
        data-callback="onCaptchaSuccess"
        data-expired-callback="onCaptchaExpired"
        sx={{ minHeight: 78 }}
      />
      {error ? (
        <Alert severity="warning" sx={{ mt: 1.5 }}>
          {error}
        </Alert>
      ) : null}
    </Box>
  );
}
