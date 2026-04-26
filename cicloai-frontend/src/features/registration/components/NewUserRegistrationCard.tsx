import { useEffect, useMemo, useState } from 'react';
import { Alert, Autocomplete, Button, MenuItem, Paper, Stack, TextField, Typography } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import type { NewUserRegistration } from '@/features/agent/types/registration';
import { bikeTeamService } from '@/features/race/services/bikeTeamService';
import type { BikeTeam } from '@/features/race/types/bikeTeam';
import { AccessRequiredAlert } from '@/components/common/AccessRequiredAlert';
import { isAccessRequiredMessage } from '@/components/common/accessRequired';
import { GenderSelectField } from '@/components/common/GenderSelectField';

const dniExtensions = [
  { label: 'Beni', value: 'BE' },
  { label: 'Chuquisaca', value: 'CH' },
  { label: 'Cochabamba', value: 'CO' },
  { label: 'La Paz', value: 'LP' },
  { label: 'Oruro', value: 'OR' },
  { label: 'Pando', value: 'PA' },
  { label: 'Potosi', value: 'PO' },
  { label: 'Santa Cruz', value: 'SC' },
  { label: 'Tarija', value: 'TJ' },
] as const;

const cyclistCategories = ['CICLOTURISTA', 'AFICIONADO', 'FEDERADO'] as const;

interface NewUserRegistrationCardProps {
  onSubmit: (registration: NewUserRegistration) => void;
}

/**
 * Rich chat card for first-time registration.
 * It keeps frontend validation close to the fields while teams remain sourced
 * from the backend catalog, preserving one source of truth for active teams.
 */
export function NewUserRegistrationCard({ onSubmit }: NewUserRegistrationCardProps) {
  const [form, setForm] = useState<NewUserRegistration>({
    dni: '',
    dniExtension: 'SC',
    fullName: '',
    email: '',
    birthDate: '',
    gender: '',
    category: '',
    team: '',
  });
  const [teams, setTeams] = useState<BikeTeam[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<BikeTeam | null>(null);
  const [loadingTeams, setLoadingTeams] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    bikeTeamService
      .getActiveTeams()
      .then(setTeams)
      .catch((currentError) => {
        setError(currentError instanceof Error ? currentError.message : 'No pudimos cargar los equipos activos.');
      })
      .finally(() => setLoadingTeams(false));
  }, []);

  const dniHasValidFormat = useMemo(() => /^\d{7}$/.test(form.dni), [form.dni]);
  const emailHasValidFormat = useMemo(
    () => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()),
    [form.email],
  );

  function updateField(field: keyof NewUserRegistration, value: string): void {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function submit(): void {
    if (!dniHasValidFormat) {
      setError('El DNI debe contener exactamente 7 digitos.');
      return;
    }

    if (!emailHasValidFormat) {
      setError('Ingresa un email válido para enviar la confirmación de inscripción.');
      return;
    }

    if (!form.fullName.trim() || !form.birthDate || !form.gender || !form.category || !form.team.trim()) {
      setError('Completa nombre, email, fecha de nacimiento, género, categoria y equipo para continuar.');
      return;
    }

    setError(null);
    onSubmit(form);
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2}>
        <Typography variant="h3">Datos del ciclista</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <TextField
            fullWidth
            label="DNI"
            value={form.dni}
            inputProps={{ inputMode: 'numeric', maxLength: 7, pattern: '[0-9]{7}' }}
            error={Boolean(form.dni) && !dniHasValidFormat}
            helperText={Boolean(form.dni) && !dniHasValidFormat ? 'Debe tener exactamente 7 digitos.' : ' '}
            onChange={(event) => updateField('dni', event.target.value.replace(/\D/g, '').slice(0, 7))}
            required
          />
          <TextField
            select
            label="EXT"
            value={form.dniExtension}
            onChange={(event) => updateField('dniExtension', event.target.value)}
            sx={{ minWidth: { xs: '100%', sm: 180 } }}
            required
          >
            {dniExtensions.map((extension) => (
              <MenuItem key={extension.value} value={extension.value}>
                {extension.label} ({extension.value})
              </MenuItem>
            ))}
          </TextField>
        </Stack>
        <TextField
          label="Nombre completo"
          value={form.fullName}
          onChange={(event) => updateField('fullName', event.target.value)}
          required
        />
        <TextField
          label="Email del participante"
          type="email"
          value={form.email}
          error={Boolean(form.email) && !emailHasValidFormat}
          helperText={Boolean(form.email) && !emailHasValidFormat ? 'Ingresa un email válido.' : ' '}
          onChange={(event) => updateField('email', event.target.value)}
          required
        />
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
          <TextField
            fullWidth
            label="Fecha de nacimiento"
            type="date"
            value={form.birthDate}
            onChange={(event) => updateField('birthDate', event.target.value)}
            InputLabelProps={{ shrink: true }}
            required
          />
          <GenderSelectField value={form.gender} onChange={(value) => updateField('gender', value)} required />
        </Stack>
        <TextField
          select
          label="Categoría"
          value={form.category}
          onChange={(event) => updateField('category', event.target.value)}
          required
        >
          {cyclistCategories.map((category) => (
            <MenuItem key={category} value={category}>
              {category}
            </MenuItem>
          ))}
        </TextField>
        <Autocomplete
          options={teams}
          value={selectedTeam}
          loading={loadingTeams}
          getOptionLabel={(option) => option.name}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          onChange={(_, value) => {
            setSelectedTeam(value);
            updateField('team', value?.name ?? '');
          }}
          renderInput={(params) => (
            <TextField {...params} label="Equipo de ciclismo / Independiente" required />
          )}
        />
        {error ? (
          isAccessRequiredMessage(error) ? <AccessRequiredAlert message={error} /> : <Alert severity="warning">{error}</Alert>
        ) : null}
        <Button variant="contained" endIcon={<ArrowForwardIcon />} onClick={submit}>
          Enviar datos al agente
        </Button>
      </Stack>
    </Paper>
  );
}
