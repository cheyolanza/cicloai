import { httpClient } from '@/services/http/httpClient';

export interface AdminLoginRequest {
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  username: string;
}

export interface AdminSessionResponse {
  username: string;
}

export const adminAuthService = {
  login(payload: AdminLoginRequest): Promise<AdminLoginResponse> {
    return httpClient<AdminLoginResponse>('/admin/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  me(authToken: string): Promise<AdminSessionResponse> {
    return httpClient<AdminSessionResponse>('/admin/me', { authToken });
  },
};
