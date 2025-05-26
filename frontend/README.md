# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

## Testing

See [TESTING.md](./TESTING.md) for a full test strategy and coverage.

### Frontend
- Run linter: `npm run lint`
- Run unit/integration tests: `npm run test`

### Backend
- Run all backend tests: `pytest`

Test coverage and details are in TESTING.md.

# Frontend Quickstart: UI Framework

## Overview
This project uses [Material UI (MUI)](https://mui.com/) for a modern, accessible, and responsive UI, following the architecture described in `docs/UI_overview`.

## Core Layout
- **MainNav**: Sidebar navigation (src/components/layout/MainNav.tsx)
- **TopBar**: Top navigation bar (src/components/layout/TopBar.tsx)
- **App Shell**: Main layout in src/App.tsx

## Shared Components
- Place all reusable UI components in `src/components/common/` (e.g., Button, Card, Modal).
- Use MUI components as a base and extend as needed.

## Creating a New Page
1. Add a new file in `src/pages/` (e.g., `MyNewPage.tsx`).
2. Use the shared layout by adding your page to the main content area in `App.tsx`.
3. Use shared components from `src/components/common/` for consistency.

## Example: Adding a New Page
```tsx
// src/pages/MyNewPage.tsx
import React from 'react';
import { Box, Typography } from '@mui/material';

const MyNewPage: React.FC = () => (
  <Box>
    <Typography variant="h4">My New Page</Typography>
    {/* Your content here */}
  </Box>
);

export default MyNewPage;
```

Then, add it to the main content area in `App.tsx` and to the navigation in `MainNav.tsx`.

## Theming
- The theme is defined in `src/presentation/design-system/theme.ts`.
- Use the `ThemeProvider` in `App.tsx` to access theme variables.

## Resources
- [Material UI Documentation](https://mui.com/)
- [React Router Documentation](https://reactrouter.com/)

---
For more details, see `docs/UI_overview`.
