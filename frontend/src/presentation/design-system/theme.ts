import { createTheme } from '@mui/material/styles';

// Color Scheme
const colors = {
  primary: {
    main: '#4A90E2', // Modern blue
    light: '#60A5FA',
    dark: '#1D4ED8',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#17A2B8', // Teal accent
    light: '#A78BFA',
    dark: '#7C3AED',
    contrastText: '#FFFFFF',
  },
  success: {
    main: '#28A745',
    light: '#4ADE80',
    dark: '#16A34A',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#FFC107',
    light: '#FBBF24',
    dark: '#D97706',
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#DC3545',
    light: '#F87171',
    dark: '#DC2626',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#17A2B8',
    light: '#60A5FA',
    dark: '#2563EB',
    contrastText: '#FFFFFF',
  },
  grey: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  nodeTypes: {
    llm: '#3B82F6',
    notebook: '#8B5CF6',
    data: '#10B981',
  },
  background: {
    default: '#F8F9FA',
    paper: '#fff',
  },
  text: {
    primary: '#343A40',
    secondary: '#6C757D',
    disabled: '#9CA3AF',
  },
  divider: '#E0E0E0',
};

// Typography
const typography = {
  fontFamily: 'Inter, Roboto, Open Sans, Arial, sans-serif',
  h1: { fontSize: 32, fontWeight: 700, lineHeight: 1.2 },
  h2: { fontSize: 24, fontWeight: 600, lineHeight: 1.3 },
  h3: { fontSize: 20, fontWeight: 500, lineHeight: 1.4 },
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
  subtitle1: {
    fontSize: '1rem',
    lineHeight: 1.5,
    letterSpacing: '0.00938em',
  },
  subtitle2: {
    fontSize: '0.875rem',
    lineHeight: 1.57,
    letterSpacing: '0.00714em',
  },
  body1: { fontSize: 16, fontWeight: 400, lineHeight: 1.7 },
  body2: { fontSize: 14, fontWeight: 400, lineHeight: 1.7 },
  button: {
    fontWeight: 500,
    fontSize: '0.875rem',
    lineHeight: 1.75,
    letterSpacing: '0.02857em',
    textTransform: 'none',
  },
  caption: { fontSize: 12, fontWeight: 400, lineHeight: 1.5 },
  overline: {
    fontSize: '0.75rem',
    lineHeight: 2.66,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase',
  },
};

// Spacing System (8px base unit)
const spacing = {
  unit: 8,
  nodePadding: 16,    // 2u
  gridGutter: 24,     // 3u
  sectionMargin: 32,  // 4u
  containerPadding: 24, // 3u
  drawerWidth: 240,   // 30u
};

// Component styles
const components = {
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
          fontFamily: 'Inter',
          fontStyle: 'normal',
          fontDisplay: 'swap',
          fontWeight: 600,
          src: 'url("/fonts/Inter-SemiBold.woff2") format("woff2")',
        },
      ],
      body: {
        backgroundColor: colors.background.default,
        color: colors.text.primary,
        margin: 0,
        padding: 0,
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      contained: {
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        boxShadow: 'none',
        backgroundImage: 'none',
      },
    },
  },
  MuiDrawer: {
    styleOverrides: {
      paper: {
        borderRight: '1px solid',
        borderColor: colors.grey[200],
      },
    },
  },
  MuiListItem: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        margin: '4px 8px',
      },
    },
  },
  MuiListItemButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        '&:hover': {
          backgroundColor: colors.grey[100],
        },
      },
    },
  },
};

// Create the theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#4A90E2', // Modern blue
      contrastText: '#fff',
    },
    secondary: {
      main: '#17A2B8', // Teal accent
      contrastText: '#fff',
    },
    success: {
      main: '#28A745',
    },
    warning: {
      main: '#FFC107',
    },
    error: {
      main: '#DC3545',
    },
    info: {
      main: '#17A2B8',
    },
    background: {
      default: '#F8F9FA',
      paper: '#fff',
    },
    text: {
      primary: '#343A40',
      secondary: '#6C757D',
    },
    divider: '#E0E0E0',
  },
  spacing: 8, // Use multiples of 8px
  typography: {
    fontFamily: 'Inter, Roboto, Open Sans, Arial, sans-serif',
    h1: { fontSize: 32, fontWeight: 700, lineHeight: 1.2 },
    h2: { fontSize: 24, fontWeight: 600, lineHeight: 1.3 },
    h3: { fontSize: 20, fontWeight: 500, lineHeight: 1.4 },
    h4: { fontWeight: 600, fontSize: 18, lineHeight: 1.4 },
    h5: { fontWeight: 600, fontSize: 16, lineHeight: 1.4 },
    h6: { fontWeight: 600, fontSize: 14, lineHeight: 1.4 },
    body1: { fontSize: 16, fontWeight: 400, lineHeight: 1.7 },
    body2: { fontSize: 14, fontWeight: 400, lineHeight: 1.7 },
    caption: { fontSize: 12, fontWeight: 400, lineHeight: 1.5 },
  },
  shape: {
    borderRadius: 8,
  },
  components,
});

// Export the design tokens for use in styled components
export const designTokens = {
  colors,
  spacing,
  typography,
  shadows: theme.shadows,
  shape: theme.shape,
};

export { theme }; 