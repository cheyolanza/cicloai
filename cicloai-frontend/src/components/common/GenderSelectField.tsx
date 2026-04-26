import { MenuItem, TextField } from '@mui/material';

interface GenderSelectFieldProps {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
}

const genderOptions = [
  { label: 'Masculino', value: 'Masculino' },
  { label: 'Femenino', value: 'Femenino' },
] as const;

/** Shared gender field used by both single and bulk registration flows. */
export function GenderSelectField({ value, onChange, required = false }: GenderSelectFieldProps) {
  return (
    <TextField
      select
      label="Genero"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      required={required}
      sx={{ minWidth: { xs: '100%', sm: 180 } }}
    >
      {genderOptions.map((option) => (
        <MenuItem key={option.value} value={option.value}>
          {option.label}
        </MenuItem>
      ))}
    </TextField>
  );
}
