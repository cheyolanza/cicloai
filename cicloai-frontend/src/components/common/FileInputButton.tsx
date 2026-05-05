import { Button } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

interface FileInputButtonProps {
  label: string;
  accept?: string;
  disabled?: boolean;
  onChange: (file: File | null) => void;
}

export function FileInputButton({ label, accept, disabled = false, onChange }: FileInputButtonProps) {
  return (
    <Button variant="outlined" component="label" startIcon={<UploadFileIcon />} disabled={disabled}>
      {label}
      <input
        hidden
        type="file"
        accept={accept}
        disabled={disabled}
        onChange={
          async (event) => {
            const file = event.target.files ? event.target.files[0] : null;
            if (!file) {
              onChange(null);
              return;
            }

            const bytes = await file.arrayBuffer();
            const fileWithBytes = new File([bytes], file.name, { type: file.type });
            onChange(fileWithBytes);
          }
        }
      />
    </Button>
  );
}
