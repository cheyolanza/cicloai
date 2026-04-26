import { Alert, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

interface AccessRequiredAlertProps {
  message: string;
}

/** Alert with a deterministic recovery path when the temporary token is missing or expired. */
export function AccessRequiredAlert({ message }: AccessRequiredAlertProps) {
  return (
    <Alert
      severity="warning"
      action={
        <Button color="inherit" size="small" component={RouterLink} to="/">
          Volver al inicio
        </Button>
      }
      sx={{ width: '100%', maxWidth: 560 }}
    >
      {message}
    </Alert>
  );
}
