# MCP Frontend Documentation

Welcome to the documentation for the MCP (Multi-Content Pipeliner) Frontend. This application provides a visual interface for creating, managing, and executing content processing workflows.

## Table of Contents

*   [Overview](#overview)
*   [Architecture](#architecture)
*   [Project Structure](#project-structure)
*   [Setup and Running](#setup-and-running)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
    *   [Running the Development Server](#running-the-development-server)
    *   [Building for Production](#building-for-production)
*   [Core Features](#core-features)
*   [Detailed Documentation](#detailed-documentation)

## Overview

The MCP Frontend is a React-based single-page application (SPA) built with TypeScript and Vite. It uses Material UI (MUI) for UI components and Zustand for state management. The core feature is a drag-and-drop workflow builder powered by ReactFlow.

## Architecture

The application follows a component-based architecture common in React projects.
-   **Presentation Layer:** Contains React components responsible for rendering the UI. These are primarily located in `frontend/src/presentation/`.
    -   `App.tsx`: The main application component, orchestrating layouts and core components.
    -   Feature components (e.g., `WorkflowBuilder`, `MCPLibrary`, `PropertiesPanel`, `ExecutionConsole`) implement specific parts of the UI.
-   **State Management:** Global application state (nodes, edges, selections, API interaction states) is managed by Zustand in `frontend/src/store/flowStore.ts`.
-   **Services:** API interactions are handled by services, primarily `frontend/src/services/flowApi.ts`, which uses `axios` to communicate with the backend.
-   **Styling:** Material UI (MUI) is used for theming and UI components. Custom styles are applied using MUI's `sx` prop or styled-components approach if needed.

## Project Structure

Key directories and files within the `frontend` folder:

-   `public/`: Static assets.
-   `src/`: Source code.
    -   `main.tsx`: Entry point of the application.
    -   `App.tsx`: Root React component.
    -   `presentation/`: UI components, further organized by features.
        -   `design-system/`: Theme and global styles.
        -   `features/chain-builder/`: Components specific to the workflow builder.
    -   `services/`: API communication logic (e.g., `flowApi.ts`).
    -   `store/`: Zustand store definitions (e.g., `flowStore.ts`).
-   `docs/`: This documentation.
-   `index.html`: Main HTML page for the SPA.
-   `package.json`: Project dependencies and scripts.
-   `vite.config.ts`: Vite build configuration.
-   `tsconfig.json`: TypeScript configuration.

## Setup and Running

### Prerequisites

-   Node.js (LTS version recommended, e.g., v18 or v20)
-   npm (comes with Node.js) or yarn

### Installation

1.  Navigate to the `frontend` directory of the project:
    ```bash
    cd path/to/your/project/frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
    (If you encounter peer dependency issues, you might need to use `npm install --legacy-peer-deps`)

### Running the Development Server

1.  From the `frontend` directory, run:
    ```bash
    npm run dev
    ```
2.  This will start the Vite development server, typically at `http://localhost:5173` (the port might vary if 5173 is in use). Open this URL in your browser.

### Building for Production

1.  From the `frontend` directory, run:
    ```bash
    npm run build
    ```
2.  This will create a `dist` directory containing the optimized static assets for deployment.

## Core Features

-   **Visual Workflow Canvas:** Drag and drop nodes, connect them to define workflows.
-   **Node Library:** Predefined node types (LLM, Notebook, Data) to build pipelines.
-   **Properties Editor:** Select nodes or edges to configure their parameters (labels, models, paths, etc.).
-   **Workflow Management:** Save, load, and execute workflows via backend API integration.
-   **Execution Console:** View logs and status of workflow executions.

## Detailed Documentation

For more in-depth information, please refer to the following documents:

-   [`data-flow.md`](./data-flow.md): Detailed explanation of application state and data flow.
-   [`components.md`](./components.md): Documentation for individual React components.
-   [`api.md`](./api.md): Information about frontend API service and backend interactions.
-   [`guides.md`](./guides.md): Guides for testing, extending, and debugging the application. 