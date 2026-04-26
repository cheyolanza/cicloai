import { Box, Typography } from '@mui/material';
import DirectionsBikeIcon from '@mui/icons-material/DirectionsBike';
import { appConfig } from '@/config/env';

export function BrandMark() {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
      <Box
        sx={{
          width: 42,
          height: 42,
          borderRadius: '50%',
          display: 'grid',
          placeItems: 'center',
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
        }}
      >
        <DirectionsBikeIcon fontSize="small" />
      </Box>
      <Typography variant="h3" component="span">
        {appConfig.appName}
      </Typography>
    </Box>
  );
}
