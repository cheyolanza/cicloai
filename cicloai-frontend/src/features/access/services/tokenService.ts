import { tokenStorage } from '@/services/storage/tokenStorage';

export interface TokenService {
  saveToken(token: string): void;
  getToken(): string | null;
  clearToken(): void;
}

/**
 * Stores the backend-issued Bearer Token after CAPTCHA verification.
 * The token is session-scoped because this phase does not implement real user
 * accounts yet; later auth can replace the storage strategy behind this API.
 */
export const tokenService: TokenService = {
  saveToken(token: string): void {
    tokenStorage.set(token);
  },
  getToken(): string | null {
    return tokenStorage.get();
  },
  clearToken(): void {
    tokenStorage.clear();
  },
};
