import { createBrowserRouter, Navigate } from 'react-router-dom';
import { App } from '@/app/App';
import { AccessPage } from '@/features/access/components/AccessPage';
import { AgentPage } from '@/features/agent/components/AgentPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <AccessPage /> },
      { path: 'agent', element: <AgentPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
