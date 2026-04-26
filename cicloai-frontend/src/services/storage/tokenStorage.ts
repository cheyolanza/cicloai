const TOKEN_KEY = 'cicloai.tempToken';

/**
 * Thin storage adapter for the temporary access token.
 * Keeping browser APIs behind this boundary makes it simple to move the token
 * to secure cookies or a FastAPI-issued session in a later phase.
 */
export const tokenStorage = {
  set(token: string): void {
    window.sessionStorage.setItem(TOKEN_KEY, token);
  },
  get(): string | null {
    return window.sessionStorage.getItem(TOKEN_KEY);
  },
  clear(): void {
    window.sessionStorage.removeItem(TOKEN_KEY);
  },
};
