# Implementation Checklist - The Train Game

## Phase 1: Foundation & Utilities 
- [x] **Map Loader (`app/utils/config_loader.py`)**
    - [x] Parse `test_grid.json`.
    - [x] Auto-wire `sibling_id` for parallel routes.
    - [x] Validate map connectivity on load.
- [x] **Graph Engine (`app/core/graph.py`)**
    - [x] BFS: Check if two cities are connected for a specific player.
    - [x] DFS (Backtracking): Calculate the longest continuous path of routes.

## Phase 2: Core Game Logic (`app/core/engine.py`)
- [x] **Initialization Logic**
    - [x] Shuffle and deal decks.
    - [x] Setup initial face-up market (with "3 wilds" flush rule).
    - [x] Initialize player objects with starting cars and cards.
- [x] **The Turn Gatekeeper**
    - [x] Verify active player and action limits.
- [x] **Action: Draw Train Cards**
    - [x] Handle blind vs. face-up selection.
    - [x] Implement deck reshuffling when empty.
    - [x] Face-up market replenishment and flush logic.
- [x] **Action: Claim Route**
    - [x] Automatic card selection logic (Prioritize colors > wilds).
    - [x] Validation: Sibling route constraints (2nd route closed in 2-3 player games).
    - [x] Score calculation and BFS goal check.
- [x] **Action: Draw Goals**
    - [x] Pop 3 cards to `pending_goals`.
    - [x] Selection logic (Minimum 1 keep).
- [x] **Final Round & Scoring**
    - [x] Final round trigger (`cars <= 2`).
    - [x] Endgame accounting (Completed vs. Incomplete goals).
    - [x] Longest path bonus award.

## Phase 3: Persistence & State
- [x] **Redis Repository (`app/persistence/redis_client.py`)**
    - [x] Initialize Redis connection pool (Simulated via Dict).
    - [x] Implement `save_game(state: GameState)` using Pydantic serialization.
    - [x] Implement `get_game(game_id: str) -> Optional[GameState]`.
    - [x] Implement `lock_game(game_id: str)` (Omitted for In-Memory as it is synchronous).

## Phase 4: Integration & Tests
- [x] **Unit Tests (`tests/unit/`)**
    - [x] Engine state transition tests.
    - [x] Graph algorithm accuracy tests.
- [x] **Simulated Game Run**
    - [x] Complete a full game play-through using the `test_grid.json`.
- [x] **Endgame Flow Test**
    - [x] Verify final round trigger and scoring logic.

## Phase 5: API & Real-Time Communication
- [x] **FastAPI Setup (`app/main.py`)**
    - [x] Basic health check and game creation endpoints.
- [x] **WebSockets (`app/api/websocket.py`)**
    - [x] Connection Manager (track active players).
    - [x] Event Router (map incoming JSON to `engine.py` functions).
- [x] **State Sanitization**
    - [x] Implement "Fog of War" logic (hide opponent hands and incomplete goals before broadcasting).
- [x] **Reconnection Logic**
    - [x] Handle `player_id` sessions so users can rejoin after a refresh.

## Phase 6: Lobby & Room Management
- [x] **Lobby Flow Implementation**
    - [x] Create `POST /games` (empty lobby).
    - [x] Create `POST /games/{id}/join` (add player to list).
    - [x] Create `POST /games/{id}/start` (initialize deck, deal, and change status to SETUP).
- [x] **Concurrency Locking**
    - [x] Implement a basic Mutex/Lock in `handle_game_event` to prevent race conditions.
- [x] **Strict Sanitization**
    - [x] Ensure `pending_goals` are strictly hidden from everyone except the owner during SETUP status.
