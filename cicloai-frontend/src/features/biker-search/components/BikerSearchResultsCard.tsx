import { Button, Paper, Stack, Typography } from '@mui/material';
import type { BikerSearchResult } from '@/features/biker-search/types/bikerSearch.types';

interface BikerSearchResultsCardProps {
  results: BikerSearchResult[];
  onSelect: (biker: BikerSearchResult) => void;
}

/** Selectable result list for previously registered bikers. */
export function BikerSearchResultsCard({ results, onSelect }: BikerSearchResultsCardProps) {
  return (
    <Stack spacing={1.25}>
      {results.map((biker) => (
        <Paper key={biker.id} variant="outlined" sx={{ p: 1.5, borderRadius: 1 }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} justifyContent="space-between">
            <Stack spacing={0.5}>
              <Typography fontWeight={800}>{biker.fullName}</Typography>
              <Typography color="text.secondary">DNI: {biker.dni}</Typography>
              <Typography color="text.secondary">Equipo: {biker.teamName ?? 'Sin equipo'}</Typography>
            </Stack>
            <Button variant="outlined" onClick={() => onSelect(biker)}>Revisar</Button>
          </Stack>
        </Paper>
      ))}
    </Stack>
  );
}
