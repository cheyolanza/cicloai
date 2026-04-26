const ACCESS_REQUIRED_MESSAGE = 'Operación no permitida. El usuario debe validarse.';

/** Identifies backend auth/session failures that require restarting at root. */
export function isAccessRequiredMessage(message: string | null | undefined): boolean {
  return Boolean(message?.includes(ACCESS_REQUIRED_MESSAGE));
}
