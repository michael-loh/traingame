# Frontend Implementation Plan: The Train Game

## 1. Technology Stack
*   **Framework:** React (Vite) + TypeScript.
*   **Styling:** Tailwind CSS for rapid UI development.
*   **Networking:** Native WebSockets (`WebSocket` API) or a hook like `react-use-websocket` for robust reconnects.
*   **Map Rendering:** Pure SVG.

## 2. Shared Data Models
The frontend will mirror the backend's Pydantic models using TypeScript Interfaces. 
*   **Requirement:** The backend `City` model must be updated to include `x` and `y` coordinates.
*   The `test_grid.json` must be updated with coordinate data.

## 3. The SVG Rendering Strategy
The map is a pure function of the backend `GameState`.

### Cities (Nodes)
*   Rendered as `<g>` (groups) containing a `<circle>` and `<text>` for the name.
*   Positioned directly at `city.x` and `city.y`.

### Routes (Edges)
*   Routes are **not** hardcoded with coordinates. They are calculated dynamically.
*   **Math:** For a route between City A and City B, calculate the angle and distance.
*   **Train Cars:** Divide the distance by the route `length` ($n$). Render $n$ SVG `<rect>` elements along that line.
*   **State:** 
    *   If `owner_id` is null: Render empty rectangles with borders matching `route.color`.
    *   If `owner_id` equals a player: Fill rectangles with the player's color.
*   **Double Routes:** If a route has a `sibling_id`, calculate the perpendicular normal vector and offset the $n$ rectangles slightly so the parallel tracks sit side-by-side.

## 4. UI Component Architecture
*   `GameLobby`: Handles the `POST /games/join` and `POST /games/start` flows. Prompts for a username.
*   `SetupModal`: A blocking overlay that forces the player to select their initial 3 goals before the `ACTIVE` phase begins.
*   `GameBoard` (SVG): The interactive map. Clicking a valid, unclaimed route triggers a `CLAIM_ROUTE` WebSocket event.
*   `PlayerHand`: A fixed bottom bar showing the player's current Train Cards (grouped by color) and active Goal Cards.
*   `MarketBoard`: A side panel showing the 5 face-up cards, the blind deck count, and the "Draw Goals" button.
*   `Scoreboard`: A top bar showing all players, their current scores, and remaining train cars.

## 5. Real-Time State Management
*   The entire UI is wrapped in a `WebSocketProvider`.
*   Incoming `GAME_UPDATE` events replace the global React state.
*   The UI is entirely "dumb" and strictly reflects the current JSON state provided by the backend. Invalid moves (like clicking a route without enough cards) will rely on the backend sending an `ERROR` event, which the UI will display as a toast notification.