# The Train Game (Ticket to Ride Clone) - Backend Specification

## 1. Architecture Overview
* **Tech Stack:** FastAPI, WebSockets, Redis (In-Memory Store), Pydantic (Data Validation).
* **Core Philosophy:** Separation of Concerns. The backend manages a pure mathematical graph and finite economy. It does *not* know about X/Y coordinates or UI rendering.
* **State Management:** Normalized state (dictionaries instead of nested lists) to ensure O(1) lookups and a single source of truth.
* **Security:** State sanitization is performed before broadcasting over WebSockets to hide opponent hands and incomplete goal cards.

## 2. Core Data Models (Pydantic)
```python
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# --- ENUMS ---
class TrainColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    WHITE = "white"
    ORANGE = "orange"
    PINK = "pink"
    WILD = "wild" # Locomotive

class RouteColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    WHITE = "white"
    ORANGE = "orange"
    PINK = "pink"
    ANY = "any" # Grey routes

class GameStatus(str, Enum):
    SETUP = "SETUP"
    ACTIVE = "active"
    FINAL_ROUND = "final_round"
    FINISHED = "finished"

# --- BASE ENTITIES ---
class City(BaseModel):
    id: str
    name: str

class Route(BaseModel):
    id: str
    node_a: str
    node_b: str
    length: int
    color: RouteColor
    required_wildcards: int = Field(default=0, ge=0)
    owner_id: Optional[str] = None
    sibling_id: Optional[str] = None # For parallel tracks

class TrainCard(BaseModel):
    id: str
    color: TrainColor

class GoalCard(BaseModel):
    id: str
    node_a: str
    node_b: str
    points: int
    is_completed: bool = False

# --- PLAYER & GAME STATE ---
class Player(BaseModel):
    player_id: str
    score: int = 0
    train_cars_remaining: int = 45
    hand: List[TrainCard] = []
    goals: List[GoalCard] = []
    pending_goals: List[GoalCard] = []

class GameState(BaseModel):
    game_id: str
    status: GameStatus = GameStatus.SETUP
    
    turn_order: List[str] = []
    current_turn_index: int = 0
    cards_drawn_this_turn: int = 0
    final_turns_remaining: int = 0
    
    cities: Dict[str, City]
    board: Dict[str, Route]
    
    train_deck: List[TrainCard] = []
    train_discard: List[TrainCard] = []
    face_up_trains: List[TrainCard] = []
    goal_deck: List[GoalCard] = []
    players: Dict[str, Player]
```

## 3. Game Phases & Logic Flow

### Initialization (The Setup)
1.  **Generate Economy:** Create exactly 110 Train Cards (12 of each standard color, 14 Wilds) with unique UUIDs. Shuffle into `train_deck`. Create and shuffle `goal_deck`.
2.  **Turn Order:** Shuffle `player_id`s and assign them to `turn_order`.
3.  **Initial Deal:** Pop 4 Train Cards to each player.
4.  **Face-Up Market:** Pop 5 cards to `face_up_trains`. (Run a loop: If 3 or more Wilds are present, flush the 5 cards to the discard pile and redraw).
5.  **Initial Goals:** Deal 3 Goal Cards to each player's `pending_goals`. Wait for players to select which ones to keep (minimum of 2).
6.  **Transition:** Set `status` to `ACTIVE`.

### Active Phase (The Loop)
A Turn Gatekeeper strictly verifies that `turn_order[current_turn_index] == player_id` before accepting any WebSocket payload. The active player takes one of three actions:

* **Draw Train Cards:** Move a card from the blind deck or face-up market to the player's hand. If a face-up Wild is drawn as the first card, the turn ends immediately. Otherwise, wait for a second draw. Replenish the face-up market immediately after a draw, triggering the "flush" rule if 3 Wilds appear.
* **Claim Route:** Validate that the route is unowned, the player has enough cars, and the card colors/wildcards spent match the route requirements. Move spent cards to `train_discard`, deduct from `train_cars_remaining`, update the route's `owner_id`, and add base points. Run a Breadth-First Search (BFS) against the player's incomplete goals; if connected, set `is_completed = True`. Turn ends.
* **Draw Goal Cards:** Move 3 cards from `goal_deck` to `pending_goals`. Player must choose to keep at least 1. Rejected cards go to the bottom of the `goal_deck`. Turn ends.

### Final Round Trigger
* **The Check:** At the end of any action in the `ACTIVE` phase, check if the active player's `train_cars_remaining <= 2`.
* **The Transition:** If true, change `status` to `FINAL_ROUND` and set `final_turns_remaining` equal to the total number of players.
* The game loop continues normally, decrementing `final_turns_remaining` by 1 at the end of every turn. When it hits `0`, change `status` to `FINISHED`.

### Finished State & Final Scoring
The WebSocket stops accepting normal gameplay actions and runs the final accounting script:

1.  **Goal Calculation:** Iterate through every player's `goals` array. If `is_completed == True`, add `points` to their score. If `is_completed == False`, subtract `points` from their score.
2.  **Longest Path (DFS):** Run a recursive backtracking Depth-First Search over each player's network. Crucially, this algorithm must track **visited edges (routes)**, not visited nodes, to allow paths to loop through cities from different directions.
3.  **Bonus Award:** Determine the highest continuous path length among all players and award a flat 10-point bonus to the winner(s).
4.  **The Reveal:** Drop the state sanitization filters and broadcast the final, completely unhidden `GameState` object to all connected WebSockets so the UI can render the post-game scoreboard and path animations.

## 4. Map Configuration
The map topology is defined in an external configuration file (JSON/YAML) and parsed during `Initialization`.
* **Nodes:** A registry of all available `City` objects.
* **Edges:** A list of connections between cities. Each connection specifies `node_a`, `node_b`, and the `length`.
* **Routes Array:** Each edge contains an array of one or more `Route` specifications (color, specific requirements).
* **Sibling Wiring:** During parsing, if an edge contains multiple routes, the engine must automatically populate the `sibling_id` fields to link them. This ensures the validation logic can enforce the "one route per player" and "small game" restrictions without complex graph traversals.
