import React from 'react';
import { Box, CssBaseline, ThemeProvider } from '@mui/material';
import { SnackbarProvider, useSnackbar } from 'notistack';
import { theme } from './presentation/design-system/theme';
import WorkflowBuilderScreen from './pages/WorkflowBuilder/WorkflowBuilderScreen';
import PersonalizedFeedScreen from './pages/Dashboard/PersonalizedFeedScreen';
import MarketplaceScreen from './pages/Marketplace/MarketplaceScreen';
import ExecutionMonitorScreen from './pages/ExecutionMonitor/ExecutionMonitorScreen';
import MainNav from './components/layout/MainNav';
import TopBar from './components/layout/TopBar';
import { Routes, Route, Navigate } from 'react-router-dom';

// Component to initialize the notifier service
const NotifierInitializer: React.FC = () => {
  const { enqueueSnackbar } = useSnackbar();
  React.useEffect(() => {
    // initializeNotifier(enqueueSnackbar); // Uncomment if needed
  }, [enqueueSnackbar]);
  return null;
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <NotifierInitializer />
        <Box sx={{ display: 'flex', height: '100vh' }}>
          <MainNav />
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <TopBar />
            <Box sx={{ flexGrow: 1, p: 3, overflow: 'auto' }}>
              <Routes>
                <Route path="/dashboard" element={<PersonalizedFeedScreen />} />
                <Route path="/marketplace" element={<MarketplaceScreen />} />
                <Route path="/workflow-builder" element={<WorkflowBuilderScreen />} />
                <Route path="/execution-monitor" element={<ExecutionMonitorScreen />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
};

export default App;
