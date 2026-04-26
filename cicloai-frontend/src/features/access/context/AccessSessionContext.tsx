import { createContext, useContext, useMemo, useState, type PropsWithChildren } from 'react';
import { tokenService } from '@/features/access/services/tokenService';

interface AccessSessionContextValue {
  hasTemporaryToken: boolean;
  createTemporarySession: (accessToken: string) => void;
  clearTemporarySession: () => void;
}

const AccessSessionContext = createContext<AccessSessionContextValue | null>(null);

/**
 * Session context for the temporary access gate. It keeps React state aligned
 * with the storage-backed token service while preserving the service boundary
 * that will later point to FastAPI-issued sessions.
 */
export function AccessSessionProvider({ children }: PropsWithChildren) {
  const [hasTemporaryToken, setHasTemporaryToken] = useState(() => Boolean(tokenService.getToken()));

  const value = useMemo<AccessSessionContextValue>(
    () => ({
      hasTemporaryToken,
      createTemporarySession: (accessToken: string) => {
        tokenService.saveToken(accessToken);
        setHasTemporaryToken(true);
      },
      clearTemporarySession: () => {
        tokenService.clearToken();
        setHasTemporaryToken(false);
      },
    }),
    [hasTemporaryToken],
  );

  return <AccessSessionContext.Provider value={value}>{children}</AccessSessionContext.Provider>;
}

export function useAccessSession(): AccessSessionContextValue {
  const context = useContext(AccessSessionContext);

  if (!context) {
    throw new Error('useAccessSession must be used within AccessSessionProvider');
  }

  return context;
}
