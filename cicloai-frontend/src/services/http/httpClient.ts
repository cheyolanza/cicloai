import { appConfig } from '@/config/env';

export interface HttpClientOptions extends RequestInit {
  authToken?: string;
}

/**
 * Minimal HTTP facade reserved for the FastAPI integration.
 * Mock services in this phase do not depend on it, but production services can
 * reuse the same contract without leaking fetch details into UI components.
 */
export async function httpClient<T>(path: string, options: HttpClientOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  if (options.authToken) {
    headers.set('Authorization', `Bearer ${options.authToken}`);
  }

  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}: ${response.statusText}`;

    try {
      const errorPayload = (await response.json()) as { detail?: string };
      message = errorPayload.detail ?? message;
    } catch {
      // Keep the HTTP status fallback when the backend does not return JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}
