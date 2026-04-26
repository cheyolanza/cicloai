import { useState } from 'react';
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SearchIcon from '@mui/icons-material/Search';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import type { ExistingUser } from '@/features/agent/types/registration';
import { userLookupService } from '@/features/agent/services/userLookupService';

interface ExistingUserSlideProps {
  onBack: () => void;
  onContinue: (user: ExistingUser) => void;
}

/**
 * Existing-user branch. Only team editing is exposed here by design, matching
 * the current business rule while allowing the lookup service to become a real
 * FastAPI search endpoint later.
 */
export function ExistingUserSlide({ onBack, onContinue }: ExistingUserSlideProps) {
  const [query, setQuery] = useState('');
  const [foundUser, setFoundUser] = useState<ExistingUser | null>(null);
  const [team, setTeam] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function search(): Promise<void> {
    setLoading(true);
    setMessage(null);
    const user = await userLookupService.searchByName(query);
    setFoundUser(user);
    setTeam(user?.team ?? '');
    setMessage(user ? null : 'No encontramos datos con ese nombre. Puedes volver y elegir inscripción nueva.');
    setLoading(false);
  }

  return (
    <Stack spacing={2} sx={{ height: '100%', justifyContent: 'center' }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
        <TextField fullWidth label="Buscar por nombre" value={query} onChange={(event) => setQuery(event.target.value)} />
        <Button variant="contained" startIcon={<SearchIcon />} disabled={!query.trim() || loading} onClick={search}>
          {loading ? 'Buscando...' : 'Buscar'}
        </Button>
      </Stack>

      {message ? <Alert severity="info">{message}</Alert> : null}

      {foundUser ? (
        <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
          <Typography variant="h3">{foundUser.fullName}</Typography>
          <Typography color="text.secondary">DNI: {foundUser.dni}</Typography>
          <Typography color="text.secondary">Nacimiento: {foundUser.birthDate}</Typography>
          <TextField fullWidth sx={{ mt: 2 }} label="Equipo editable" value={team} onChange={(event) => setTeam(event.target.value)} />
        </Box>
      ) : null}

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
        <Button fullWidth variant="outlined" startIcon={<ArrowBackIcon />} onClick={onBack}>
          Volver
        </Button>
        <Button
          fullWidth
          variant="contained"
          endIcon={<ArrowForwardIcon />}
          disabled={!foundUser || !team.trim()}
          onClick={() => foundUser && onContinue({ ...foundUser, team })}
        >
          Continuar al pago
        </Button>
      </Stack>
    </Stack>
  );
}
