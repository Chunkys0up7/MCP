import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Sidebar from './components/Sidebar';
import Toolbar from './components/Toolbar';
import ChainBuilder from './pages/ChainBuilder';
import Dashboard from './pages/Dashboard';
import PropertiesPanel from './components/PropertiesPanel';
import ExecutionConsole from './components/ExecutionConsole';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Box display="flex" height="100vh">
          <Sidebar />
          <Box flex={1} display="flex" flexDirection="column">
            <Toolbar />
            <Box display="flex" flex={1}>
              <Box flex={3}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/chain-builder" element={<ChainBuilder />} />
                  {/* Add more routes as needed */}
                </Routes>
              </Box>
              <Box flex={1} borderLeft={1} borderColor="divider">
                <PropertiesPanel />
              </Box>
            </Box>
            <ExecutionConsole />
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App; 