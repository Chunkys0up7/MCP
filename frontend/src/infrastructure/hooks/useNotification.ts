import { useContext } from 'react';
import { NotificationContext } from '../context/NotificationContext';

export const useNotification = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error(
      'useNotification must be used within a NotificationProvider. ' +
      'Make sure your component is wrapped with NotificationProvider.'
    );
  }
  
  return context;
}; 