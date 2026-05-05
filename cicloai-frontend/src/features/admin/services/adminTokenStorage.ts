const ADMIN_TOKEN_KEY = 'cicloai.adminToken';

export const adminTokenStorage = {
  set(token: string): void {
    window.sessionStorage.setItem(ADMIN_TOKEN_KEY, token);
  },
  get(): string | null {
    return window.sessionStorage.getItem(ADMIN_TOKEN_KEY);
  },
  clear(): void {
    window.sessionStorage.removeItem(ADMIN_TOKEN_KEY);
  },
};
