import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0b79ee',
    },
    background: {
      default: '#101923',
      paper: '#1a2533',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a0aec0',
    },
    divider: '#314c68',
  },
  typography: {
    fontFamily: 'Inter, "Noto Sans", sans-serif',
    h1: {
      fontSize: '22px',
      fontWeight: 700,
      letterSpacing: '-0.015em',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '18px',
      fontWeight: 700,
      letterSpacing: '-0.015em',
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '16px',
      fontWeight: 700,
      letterSpacing: '-0.015em',
      lineHeight: 1.2,
    },
    body1: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: 1.5,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '9999px',
          textTransform: 'none',
          fontWeight: 700,
          letterSpacing: '0.015em',
          padding: '8px 16px',
          minWidth: '84px',
          maxWidth: '480px',
        },
        contained: {
          backgroundColor: '#0b79ee',
          '&:hover': {
            backgroundColor: '#0a6ad4',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1a2533',
          borderColor: '#314c68',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a2533',
          borderColor: '#314c68',
        },
      },
    },
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: '#314c68',
          '&.Mui-checked': {
            color: '#0b79ee',
          },
        },
      },
    },
  },
});

export default theme; 