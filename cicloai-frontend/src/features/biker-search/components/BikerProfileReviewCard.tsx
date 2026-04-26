import { useEffect, useState } from 'react';
import { Alert, Autocomplete, Button, Divider, Paper, Stack, TextField, Typography } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { BikerLookupActionResult, BikerSearchResult } from '@/features/biker-search/types/bikerSearch.types';
import type { CyclingTeam } from '@/features/teams/types/team.types';
import { teamService } from '@/features/teams/services/teamService';
import { bikerSearchService } from '@/features/biker-search/services/bikerSearchService';
import { AccessRequiredAlert } from '@/components/common/AccessRequiredAlert';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';

interface BikerProfileReviewCardProps {
  biker: BikerSearchResult;
  bikeRaceId?: string;
  searchedName: string;
  onCompleted: (result: BikerLookupActionResult) => void;
}

/** Review-only profile card. Only team is editable by design. */
export function BikerProfileReviewCard({ biker, bikeRaceId, searchedName, onCompleted }: BikerProfileReviewCardProps) {
  const [teams, setTeams] = useState<CyclingTeam[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<CyclingTeam | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    teamService
      .getActiveTeams()
      .then((activeTeams) => {
        setTeams(activeTeams);
        setSelectedTeam(activeTeams.find((team) => team.name.toUpperCase() === (biker.teamName ?? '').toUpperCase()) ?? null);
      })
      .catch((currentError) => {
        setError(currentError instanceof Error ? currentError.message : 'No pudimos cargar los equipos activos.');
      });
  }, [biker.teamName]);

  async function confirmUpdate(): Promise<void> {
    if (!selectedTeam) return;

    setLoading(true);
    setError(null);
    try {
      const result = await bikerSearchService.registerLookupAction(biker.id, {
        bikeRaceId,
        searchedName,
        newTeamName: selectedTeam.name,
        confirmAction: true,
      });
      onCompleted(result);
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : 'No pudimos actualizar el equipo.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
      <Stack spacing={1.5}>
        <Typography variant="h3">Datos encontrados</Typography>
        <Typography><strong>Nombre:</strong> {biker.fullName}</Typography>
        <Typography><strong>DNI:</strong> {biker.dni}</Typography>
        <Typography><strong>Fecha de nacimiento:</strong> {biker.birthDate}</Typography>
        <Typography><strong>Celular:</strong> {biker.cellphone ?? 'No registrado'}</Typography>
        <Typography><strong>Categoría:</strong> {biker.category}</Typography>
        <Typography><strong>Última carrera:</strong> {biker.lastRegisteredRace?.name ?? 'No disponible'}</Typography>
        <Divider />
        <Autocomplete
          options={teams}
          value={selectedTeam}
          getOptionLabel={(option) => option.name}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          onChange={(_, value) => setSelectedTeam(value)}
          renderInput={(params) => <TextField {...params} label="Equipo" required />}
        />
        {error ? (
          isAccessRequiredMessage(error) ? <AccessRequiredAlert message={error} /> : <Alert severity="warning">{error}</Alert>
        ) : null}
        <Button variant="contained" startIcon={<CheckCircleIcon />} disabled={!selectedTeam || loading} onClick={confirmUpdate}>
          {loading ? 'Confirmando...' : 'Confirmar actualización'}
        </Button>
      </Stack>
    </Paper>
  );
}
