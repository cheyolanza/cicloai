import type { PropsWithChildren } from 'react';
import { Box, Container } from '@mui/material';

interface FullScreenFlowLayoutProps extends PropsWithChildren {
  maxWidth?: 'sm' | 'md' | 'lg';
}

/**
 * Shared shell for the guided flows. It owns viewport height and overflow
 * rules so individual slides can stay focused on behavior instead of layout
 * mechanics.
 */
export function FullScreenFlowLayout({ children, maxWidth = 'md' }: FullScreenFlowLayoutProps) {
  return (
    <Box
      component="main"
      sx={{
        height: '100dvh',
        overflow: 'hidden',
        bgcolor: 'background.default',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <Container maxWidth={maxWidth} sx={{ height: '100%', py: { xs: 2, md: 4 } }}>
        {children}
      </Container>
    </Box>
  );
}
