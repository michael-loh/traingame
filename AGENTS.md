# Agent Guidelines - The Train Game (Global)

## 1. Project Overview
The Train Game is a real-time, high-performance "Ticket to Ride" clone. It is built as a monorepo containing a Python backend and a TypeScript frontend.

## 2. Tech Stack
*   **Backend:** Python 3.x, FastAPI, WebSockets, Pydantic, Pytest.
*   **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, `react-use-websocket`.
*   **Communication:** JSON over WebSockets for real-time state synchronization.

## 3. Directory Structure
*   `backend/`: Contains the game engine, API endpoints, and persistence logic. (See `backend/AGENTS.md`)
*   `frontend/`: Contains the React UI and client-side game state management. (See `frontend/AGENTS.md`)
*   `train_game_plan.md`: The central source of truth for game rules and architecture.

## 4. Cross-Cutting Principles
*   **Source of Truth:** The Backend is the ultimate authority on game state. The Frontend is a reactive view of that state.
*   **Consistency:** Keep the `GameState` TypeScript interfaces in `frontend/src/types/game.ts` perfectly synced with the Pydantic models in `backend/app/models/game.py`.
*   **Atomic PRs:** When adding a feature that requires both backend and frontend changes, implement the backend logic and state updates first.
