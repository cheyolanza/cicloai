/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME?: string;
  readonly VITE_ENABLE_MOCKS?: string;
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_RECAPTCHA_ENTERPRISE_SITE_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Window {
  onCaptchaSuccess?: (token: string) => void;
  onCaptchaExpired?: () => void;
  grecaptcha?: {
    enterprise: {
      ready: (callback: () => void) => void;
      render: (
        container: HTMLElement,
        parameters: {
          sitekey: string;
          action: string;
          callback?: (token: string) => void;
          'expired-callback'?: () => void;
          'error-callback'?: () => void;
        },
      ) => number;
      getResponse: (widgetId?: number) => string;
      reset: (widgetId?: number) => void;
    };
  };
}
