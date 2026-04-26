import { useState } from 'react';
import { IconButton, TextField } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface AgentChatInputProps {
  disabled: boolean;
  onSend: (message: string) => void;
}

/** Bottom composer enabled only while the user is in free RAG conversation mode. */
export function AgentChatInput({ disabled, onSend }: AgentChatInputProps) {
  const [message, setMessage] = useState('');

  function submit(): void {
    const trimmed = message.trim();
    if (!trimmed || disabled) return;
    setMessage('');
    onSend(trimmed);
  }

  return (
    <TextField
      fullWidth
      disabled={disabled}
      placeholder={disabled ? 'Usa las opciones sugeridas o completa el flujo activo.' : 'Escribe tu pregunta sobre la convocatoria...'}
      value={message}
      onChange={(event) => setMessage(event.target.value)}
      onKeyDown={(event) => {
        if (event.key === 'Enter') {
          event.preventDefault();
          submit();
        }
      }}
      InputProps={{
        endAdornment: (
          <IconButton disabled={disabled || !message.trim()} onClick={submit}>
            <SendIcon />
          </IconButton>
        ),
      }}
    />
  );
}
