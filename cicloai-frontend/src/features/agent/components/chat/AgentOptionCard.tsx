import { Button, Stack } from '@mui/material';
import type { RegistrationType } from '@/features/agent/types/registration';

interface AgentOptionCardProps {
  options: Array<{ label: string; value: RegistrationType }>;
  onSelect: (value: RegistrationType) => void;
}

/** Quick replies rendered as agent-suggested actions inside the chat. */
export function AgentOptionCard({ options, onSelect }: AgentOptionCardProps) {
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
      {options.map((option) => (
        <Button key={option.value} variant="contained" onClick={() => onSelect(option.value)}>
          {option.label}
        </Button>
      ))}
    </Stack>
  );
}
