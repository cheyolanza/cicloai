import type { PropsWithChildren } from 'react';
import { Box, Card, LinearProgress, Stack, Typography } from '@mui/material';
import { BrandMark } from '@/components/common/BrandMark';

interface WizardFrameProps extends PropsWithChildren {
  title: string;
  subtitle?: string;
  progress: number;
}

/**
 * Stable visual frame for all agent slides. Fixed min/max dimensions prevent
 * layout jumps while each step replaces the previous one inside the same area.
 */
export function WizardFrame({ title, subtitle, progress, children }: WizardFrameProps) {
  return (
    <Stack sx={{ height: '100%', justifyContent: 'center' }} spacing={2}>
      <BrandMark />
      <Card
        elevation={0}
        sx={{
          border: '1px solid',
          borderColor: 'divider',
          height: { xs: 'calc(100dvh - 112px)', md: 'min(720px, calc(100dvh - 128px))' },
          display: 'grid',
          gridTemplateRows: 'auto auto 1fr',
          overflow: 'hidden',
        }}
      >
        <Box sx={{ px: { xs: 2.5, md: 4 }, pt: { xs: 2.5, md: 3 } }}>
          <Typography variant="h2">{title}</Typography>
          {subtitle ? (
            <Typography color="text.secondary" sx={{ mt: 0.75 }}>
              {subtitle}
            </Typography>
          ) : null}
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ mt: 2 }} />
        <Box sx={{ p: { xs: 2.5, md: 4 }, minHeight: 0, overflow: 'hidden' }}>{children}</Box>
      </Card>
    </Stack>
  );
}
