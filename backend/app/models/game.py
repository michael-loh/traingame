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
    LOBBY = "lobby"
    SETUP = "setup"
    ACTIVE = "active"
    FINAL_ROUND = "final_round"
    FINISHED = "finished"

# --- BASE ENTITIES ---
class City(BaseModel):
    id: str
    name: str
    x: float # 0-100 percentage
    y: float # 0-100 percentage

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
    secret_token: str # Used for authentication and rejoin
    score: int = 0
    train_cars_remaining: int = 45
    hand: List[TrainCard] = []
    goals: List[GoalCard] = []
    pending_goals: List[GoalCard] = []

class GameState(BaseModel):
    game_id: str
    status: GameStatus = GameStatus.LOBBY
    
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
