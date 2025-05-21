import { createTheme } from '@mui/material/styles';

// Color Scheme
const colors = {
  primary: '#2563EB',    // Primary Action
  success: '#22C55E',    // Success
  warning: '#F59E0B',    // Warning
  error: '#EF4444',      // Error
  nodeTypes: {
    llm: '#3B82F6',      // LLM nodes
    notebook: '#8B5CF6',  // Notebook nodes
    data: '#10B981',     // Data nodes
  }
};

// Typography
const typography = {
  fontFamily: [
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'Roboto',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"',
  ].join(','),
  h1: {
    fontWeight: 600,
    fontSize: '2.5rem',
    lineHeight: 1.2,
  },
  h2: {
    fontWeight: 600,
    fontSize: '2rem',
    lineHeight: 1.3,
  },
  h3: {
    fontWeight: 600,
    fontSize: '1.75rem',
    lineHeight: 1.4,
  },
  h4: {
    fontWeight: 600,
    fontSize: '1.5rem',
    lineHeight: 1.4,
  },
  h5: {
    fontWeight: 600,
    fontSize: '1.25rem',
    lineHeight: 1.4,
  },
  h6: {
    fontWeight: 600,
    fontSize: '1rem',
    lineHeight: 1.4,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5,
  },
  button: {
    fontWeight: 500,
    fontSize: '0.875rem',
    lineHeight: 1.75,
    textTransform: 'none' as const,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.66,
  },
  overline: {
    fontSize: '0.75rem',
    lineHeight: 2.66,
    textTransform: 'uppercase' as const,
  },
};

// Spacing System (8px base unit)
const spacing = {
  unit: 8,
  nodePadding: 16,    // 2u
  gridGutter: 24,     // 3u
  sectionMargin: 32,  // 4u
};

// Create the theme
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#9c27b0',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
    info: {
      main: '#2196f3',
    },
    success: {
      main: '#4caf50',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography,
  spacing: spacing.unit,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '@font-face': [
          {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: 400,
            src: 'url("/fonts/Inter-Regular.woff2") format("woff2")',
          },
          {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: 500,
            src: 'url("/fonts/Inter-Medium.woff2") format("woff2")',
          },
          {
            fontFamily: 'IBM Plex Sans',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: 600,
            src: 'url("/fonts/IBMPlexSans-SemiBold.woff2") format("woff2")',
          },
          {
            fontFamily: 'Fira Code',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: 400,
            src: 'url("/fonts/FiraCode-Regular.woff2") format("woff2")',
          },
        ],
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Export the design tokens for use in styled components
export const designTokens = {
  colors,
  spacing,
  typography,
}; 