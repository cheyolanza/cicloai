import { Button } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

interface FileInputButtonProps {
  label: string;
  accept?: string;
  onChange: (file: File | null) => void;
}

export function FileInputButton({ label, accept, onChange }: FileInputButtonProps) {
  return (
    <Button variant="outlined" component="label" startIcon={<UploadFileIcon />}>
      {label}
      <input
        hidden
        type="file"
        accept={accept}
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
      />
    </Button>
  );
}
