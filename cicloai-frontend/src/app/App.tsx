import { Outlet } from 'react-router-dom';
import { AccessSessionProvider } from '@/features/access/context/AccessSessionContext';

export function App() {
  return (
    <AccessSessionProvider>
      <Outlet />
    </AccessSessionProvider>
  );
}
