import { appConfig } from '@/config/env';
import { httpClient } from '@/services/http/httpClient';

export interface CaptchaValidationResult {
  valid: boolean;
  provider: 'recaptcha-enterprise';
  token: string;
  action: string;
  accessToken: string;
  expiresIn: number;
}

export interface CaptchaService {
  validate(token: string, action: string): Promise<CaptchaValidationResult>;
  getWidgetToken(): string | null;
}

interface BackendCaptchaVerificationResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

async function verifyTokenWithBackend(captchaToken: string): Promise<BackendCaptchaVerificationResponse> {
  return httpClient<BackendCaptchaVerificationResponse>('/security/captcha/verify', {
    method: 'POST',
    body: JSON.stringify({ captcha_token: captchaToken }),
  });
}

/**
 * CAPTCHA adapter that exchanges the Google token for a backend-issued JWT.
 * With frontend mocks enabled we still call FastAPI, but send the backend mock
 * token so the rest of the app exercises the real Bearer Token flow.
 */
export const captchaService: CaptchaService = {
  getWidgetToken(): string | null {
    const token = window.grecaptcha?.enterprise.getResponse();
    return token || null;
  },
  async validate(token: string, action: string): Promise<CaptchaValidationResult> {
    const captchaToken = appConfig.enableMocks ? 'mock-valid-captcha' : token;
    const response = await verifyTokenWithBackend(captchaToken);

    return {
      valid: Boolean(response.access_token),
      provider: 'recaptcha-enterprise',
      token,
      action,
      accessToken: response.access_token,
      expiresIn: response.expires_in,
    };
  },
};
