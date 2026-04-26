export const appConfig = {
  appName: import.meta.env.VITE_APP_NAME ?? 'CicloAI',
  enableMocks: import.meta.env.VITE_ENABLE_MOCKS !== 'false',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  recaptchaEnterpriseSiteKey:
    import.meta.env.VITE_RECAPTCHA_ENTERPRISE_SITE_KEY ?? '6LcYJMcsAAAAANnSzsP1VP4bJ86DKcGQzhVbZNO2',
} as const;
