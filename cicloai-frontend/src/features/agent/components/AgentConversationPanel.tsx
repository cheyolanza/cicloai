import type { ReactNode } from 'react';
import { Box, Paper, Stack, Typography } from '@mui/material';

interface AgentConversationPanelProps {
  children: ReactNode;
  input: ReactNode;
}

/** Shared framed panel for the chat timeline and bottom composer. */
export function AgentConversationPanel({ children, input }: AgentConversationPanelProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        height: 'calc(100dvh - 104px)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#F9FBFA',
      }}
    >
      <Box sx={{ px: { xs: 2, md: 3 }, py: 1.5, borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Typography variant="h2">Agente CicloAI</Typography>
        <Typography color="text.secondary">Inscripción conversacional a competencias de ciclismo</Typography>
      </Box>
      {children}
      <Box sx={{ p: { xs: 1.5, md: 2 }, borderTop: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Stack>{input}</Stack>
      </Box>
    </Paper>
  );
}
