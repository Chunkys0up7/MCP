import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './presentation/design-system/theme';
import { NotificationProvider } from './infrastructure/context/NotificationContext';
import { ErrorBoundary } from './presentation/components/ErrorBoundary';
import Sidebar from './presentation/features/navigation/Sidebar';
import WorkspaceLayout from './presentation/features/chain-builder/WorkspaceLayout';
import { ChainServiceImpl } from './infrastructure/services/chainService';

// Initialize services
const chainService = new ChainServiceImpl(import.meta.env.VITE_API_URL || 'http://localhost:3000/api');

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <NotificationProvider>
        <ErrorBoundary>
          <Router>
            <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
              <Sidebar />
              <main style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <Routes>
                  <Route path="/" element={<WorkspaceLayout />} />
                  <Route path="/create-mcp" element={<div>Create MCP Page</div>} />
                  <Route path="/manage-mcps" element={<div>Manage MCPs Page</div>} />
                  <Route path="/test-mcps" element={<div>Test MCPs Page</div>} />
                  <Route path="/settings" element={<div>Settings Page</div>} />
                </Routes>
              </main>
            </div>
          </Router>
        </ErrorBoundary>
      </NotificationProvider>
    </ThemeProvider>
  );
};

export default App;
