import React from 'react';
import ReactDOM from 'react-dom/client';
import { initializeMonitoring } from './monitoring/setup';
import App from './App';
import './index.css';

// Initialize monitoring
initializeMonitoring();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
