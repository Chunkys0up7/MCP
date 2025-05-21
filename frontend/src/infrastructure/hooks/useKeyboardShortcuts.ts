import { useEffect, useCallback } from 'react';

type KeyCombo = string;
type ShortcutHandler = (event: KeyboardEvent) => void;

interface ShortcutMap {
  [key: KeyCombo]: ShortcutHandler;
}

export const useKeyboardShortcuts = (shortcuts: ShortcutMap) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Ignore if user is typing in an input or textarea
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      const keyCombo = [
        event.ctrlKey && 'Ctrl',
        event.altKey && 'Alt',
        event.shiftKey && 'Shift',
        event.key,
      ]
        .filter(Boolean)
        .join('+');

      const handler = shortcuts[keyCombo];
      if (handler) {
        event.preventDefault();
        handler(event);
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}; 