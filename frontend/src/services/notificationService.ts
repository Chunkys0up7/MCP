import { OptionsObject, SnackbarKey, SnackbarMessage } from 'notistack';

// Define a type for the enqueueSnackbar function
type EnqueueSnackbarType = (message: SnackbarMessage, options?: OptionsObject) => SnackbarKey;

// Hold a reference to the enqueueSnackbar function from notistack
let enqueueSnackbarRef: EnqueueSnackbarType | null = null;

/**
 * Initializes the notification service with the enqueueSnackbar function from notistack.
 * This should be called once in the main App component after SnackbarProvider is mounted.
 * @param {EnqueueSnackbarType} enqueueSnackbar - The enqueueSnackbar function provided by notistack's useSnackbar hook.
 */
export const initializeNotifier = (enqueueSnackbar: EnqueueSnackbarType): void => {
  enqueueSnackbarRef = enqueueSnackbar;
};

/**
 * Utility to dispatch notifications.
 * Ensures that the notifier has been initialized before attempting to show a snackbar.
 */
const dispatchNotification = (message: SnackbarMessage, options?: OptionsObject): SnackbarKey | null => {
  if (!enqueueSnackbarRef) {
    console.error('Notification service not initialized. Did you call initializeNotifier?');
    // Fallback to console.log if notifier is not available
    const level = options?.variant || 'info';
    console.log(`[${level.toUpperCase()}] NOTIFY (fallback):`, message);
    return null;
  }
  return enqueueSnackbarRef(message, options);
}

export const notify = {
  success: (message: SnackbarMessage): SnackbarKey | null =>
    dispatchNotification(message, { variant: 'success' }),
  error: (message: SnackbarMessage): SnackbarKey | null =>
    dispatchNotification(message, { variant: 'error' }),
  info: (message: SnackbarMessage): SnackbarKey | null =>
    dispatchNotification(message, { variant: 'info' }),
  warning: (message: SnackbarMessage): SnackbarKey | null =>
    dispatchNotification(message, { variant: 'warning' }),
};

// Example of more specific notifications if needed:
// export const notifyApiError = (message: string = "An API error occurred.", error?: any) => {
//   let detailedMessage = message;
//   if (error && error.message) {
//     detailedMessage += `: ${error.message}`;
//   } else if (typeof error === 'string') {
//     detailedMessage += `: ${error}`;
//   }
//   console.error("API Error:", error); // Also log the full error
//   return dispatchNotification(detailedMessage, { variant: 'error' });
// }; 