# Agent Guidelines - Frontend (The Train Game)

## 1. Development Environment
*   **Node.js:** Ensure you are using a modern LTS version of Node.
*   **Package Manager:** Use `npm`.
*   **Commands:**
    *   `npm install`: Install dependencies.
    *   `npm run dev`: Start the development server.
    *   `npm run build`: Perform type checking and production build.

## 2. Architectural Mandates
*   **Reactive UI:** The UI should be a pure reflection of the `GameState` received via WebSockets.
*   **State Management:** Use `GameContext` (found in `src/context/GameContext.tsx`) for global game state. Avoid drilling props where possible.
*   **WebSocket Integration:** Use `react-use-websocket` for communication. All outgoing player actions should be sent as `GameEvent` objects.

## 3. UI Development (Demo Mode)
*   **Isolated Workflow:** Use Demo Mode (`http://localhost:5173/?demo=true`) for UI/UX work to avoid backend dependencies.
*   **Mock State:** Keep `src/mocks/gameState.ts` updated when the `GameState` interface changes.

## 4. Coding Standards (Style & Quality)
*   **Functional Components:** Use functional components with hooks exclusively.
*   **TypeScript:** Strict typing is required. Avoid `any`. Ensure all component props are interface-defined.
*   **Styling:** Use **Tailwind CSS** for layout and styling. Prefer utility classes over custom CSS.
*   **Formatting:** Follow the project's ESLint and Prettier configurations. Run `npm run lint` before committing.
*   **Component Structure:** Keep components small and focused. Extract sub-components (e.g., `PlayerCard`, `RouteLine`) into `src/components/`.

## 5. Testing & Validation
*   **Type Safety:** Always run `npm run build` to verify there are no TypeScript errors.
*   **Visual Polish:** Ensure animations are smooth and the UI handles various screen sizes (responsive design).
