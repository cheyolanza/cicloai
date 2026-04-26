import { Button, Chip, Stack, Typography } from '@mui/material';
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1';
import ManageSearchIcon from '@mui/icons-material/ManageSearch';
import GroupsIcon from '@mui/icons-material/Groups';
import type { Race } from '@/features/race/types/race';
import type { RegistrationType } from '@/features/agent/types/registration';

interface RaceSelectionSlideProps {
  race: Race;
  onSelect: (type: RegistrationType) => void;
}

/**
 * Entry slide for the agent. It presents backend-provided race metadata and
 * captures the branch that drives the rest of the registration state machine.
 */
export function RaceSelectionSlide({ race, onSelect }: RaceSelectionSlideProps) {
  return (
    <Stack spacing={3} sx={{ height: '100%', justifyContent: 'center' }}>
      <Stack spacing={1}>
        <Chip label="Carrera habilitada" color="primary" sx={{ alignSelf: 'flex-start' }} />
        <Typography variant="h1">{race.name}</Typography>
        <Typography color="text.secondary">
          {race.date ? `Fecha: ${new Date(`${race.date}T00:00:00`).toLocaleDateString('es-BO')}. ` : ''}
          {race.description}
        </Typography>
      </Stack>

      <Typography variant="h3">¿Qué tipo de inscripción deseas realizar?</Typography>

      <Stack spacing={1.5}>
        <Button variant="contained" size="large" startIcon={<PersonAddAlt1Icon />} onClick={() => onSelect('new')}>
          Es mi primera carrera
        </Button>
        <Button variant="outlined" size="large" startIcon={<ManageSearchIcon />} onClick={() => onSelect('existing')}>
          Ya me inscribí antes, deseo buscar mis datos
        </Button>
        <Button variant="outlined" size="large" startIcon={<GroupsIcon />} onClick={() => onSelect('bulk')}>
          Deseo inscribir a varios ciclistas
        </Button>
      </Stack>
    </Stack>
  );
}
