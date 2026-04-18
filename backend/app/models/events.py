from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel

class EventType(str, Enum):
    # Incoming (Client -> Server)
    CHOOSE_GOALS = "CHOOSE_GOALS"
    DRAW_TRAIN_CARD = "DRAW_TRAIN_CARD"
    CLAIM_ROUTE = "CLAIM_ROUTE"
    DRAW_GOAL_CARDS = "DRAW_GOAL_CARDS"
    
    # Outgoing (Server -> Client)
    GAME_UPDATE = "GAME_UPDATE"
    ERROR = "ERROR"

class GameEvent(BaseModel):
    type: EventType
    payload: Dict[str, Any]

# Payload Schemas for Validation
class ChooseGoalsPayload(BaseModel):
    kept_goal_ids: List[str]

class DrawTrainCardPayload(BaseModel):
    card_id: Optional[str] = None # None for blind draw

class ClaimRoutePayload(BaseModel):
    route_id: str
    card_ids: List[str]

class ErrorPayload(BaseModel):
    message: str
