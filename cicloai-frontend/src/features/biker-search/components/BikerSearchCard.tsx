import { useState } from 'react';
import { Alert, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import type { BikerLookupActionResult, BikerSearchResult } from '@/features/biker-search/types/bikerSearch.types';
import { bikerSearchService } from '@/features/biker-search/services/bikerSearchService';
import { BikerSearchResultsCard } from '@/features/biker-search/components/BikerSearchResultsCard';
import { BikerProfileReviewCard } from '@/features/biker-search/components/BikerProfileReviewCard';
import { AccessRequiredAlert } from '@/components/common/AccessRequiredAlert';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';

interface BikerSearchCardProps {
  bikeRaceId?: string;
  onCompleted: (result: BikerLookupActionResult) => void;
}

/** Chat-embedded existing-biker lookup flow. It never creates a new race registration. */
export function BikerSearchCard({ bikeRaceId, onCompleted }: BikerSearchCardProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<BikerSearchResult[]>([]);
  const [selectedBiker, setSelectedBiker] = useState<BikerSearchResult | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function search(): Promise<void> {
    setLoading(true);
    setError(null);
    setMessage(null);
    setSelectedBiker(null);

    try {
      const response = await bikerSearchService.searchByName(query);
      if (response.status === 'not_found') {
        setResults([]);
        setMessage(response.message);
      } else {
        setResults(response.results);
      }
    } catch (currentError) {
      setResults([]);
      setError(currentError instanceof Error ? currentError.message : 'No pudimos buscar ciclistas.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2}>
        <Typography variant="h3">Buscar datos registrados</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <TextField fullWidth label="Nombre del ciclista" value={query} onChange={(event) => setQuery(event.target.value)} />
          <Button variant="contained" startIcon={<SearchIcon />} disabled={query.trim().length < 2 || loading} onClick={search}>
            {loading ? 'Buscando...' : 'Buscar'}
          </Button>
        </Stack>
        {message ? <Alert severity="info">{message}</Alert> : null}
        {error ? (
          isAccessRequiredMessage(error) ? <AccessRequiredAlert message={error} /> : <Alert severity="warning">{error}</Alert>
        ) : null}
        {results.length > 0 && !selectedBiker ? <BikerSearchResultsCard results={results} onSelect={setSelectedBiker} /> : null}
        {selectedBiker ? (
          <BikerProfileReviewCard
            biker={selectedBiker}
            bikeRaceId={bikeRaceId}
            searchedName={query}
            onCompleted={onCompleted}
          />
        ) : null}
      </Stack>
    </Paper>
  );
}
