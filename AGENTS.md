# Agent Guidelines - The Train Game

## 1. Project Structure
The project is structured as a monorepo with sibling directories:
*   `backend/`: FastAPI application, engine logic, and tests.
*   `frontend/`: React + Vite application.

## 2. Development Environment
*   **Virtual Environments:** Always use a Python virtual environment (`venv`) inside the `backend/` directory.
    *   **Setup:** `cd backend && python -m venv venv`
    *   **Activation (Windows):** `.\venv\Scripts\activate`
*   **Node Version:** Use a modern Node.js version inside the `frontend/` directory.

## 3. Architectural Mandates
*   **Separation of Concerns:** The backend is a pure mathematical engine. Do not introduce logic related to UI layout or rendering.
*   **Statelessness:** The FastAPI application remains stateless; all game state must be persisted in the `repository`.
*   **Immutability:** Treat GameState as immutable. Use Pydantic's `model_copy(update=...)` for updates.

## 4. UI Development (Demo Mode)
*   **Isolated Testing:** When working on UI/UX, prefer using **Demo Mode** (`http://localhost:5173/?demo=true`). This uses `frontend/src/mocks/gameState.ts` to provide a full game state without requiring a backend.
*   **State Alignment:** Ensure any new UI features are mapped to the standard `GameState` interface in `frontend/src/types/game.ts`.

## 5. Coding Standards
*   **Type Safety:** All functions must have complete type hints. Use `Pydantic` for data validation and `Enum`s for categories (Colors, Statuses).
*   **Error Handling:** Rule violations should be caught and transformed into clear WebSocket error messages via `manager.send_error`.

## 6. Testing Principles
*   **Mandatory Verification:** ALWAYS run the full test suite (`python -m pytest`) inside the `backend/` directory after any backend change.
*   **Logic First:** Every new game mechanic must be accompanied by a unit test that verifies the `GameState` transition.

## 7. Communication
*   **Atomic Updates:** Keep changes surgical and focused on the specific task.
*   **Documentation:** Update `train_game_plan.md` if an architectural change is made.
