import { useState } from 'react';
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import type { ExistingUser } from '@/features/agent/types/registration';
import { userLookupService } from '@/features/agent/services/userLookupService';

interface ExistingUserSearchCardProps {
  onSubmit: (user: ExistingUser) => void;
}

/** Embedded card that lets the agent recover an existing cyclist profile. */
export function ExistingUserSearchCard({ onSubmit }: ExistingUserSearchCardProps) {
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
    setMessage(user ? null : 'No encontramos datos con ese nombre. Puedes intentar con otro nombre.');
    setLoading(false);
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2}>
        <Typography variant="h3">Buscar inscripción anterior</Typography>
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
        <Button
          variant="contained"
          endIcon={<ArrowForwardIcon />}
          disabled={!foundUser || !team.trim()}
          onClick={() => foundUser && onSubmit({ ...foundUser, team })}
        >
          Usar estos datos
        </Button>
      </Stack>
    </Paper>
  );
}
