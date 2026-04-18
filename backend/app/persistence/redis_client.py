import json
from abc import ABC, abstractmethod
from typing import Dict, Optional
from app.models.game import GameState

class GameRepository(ABC):
    @abstractmethod
    def save_game(self, state: GameState):
        pass

    @abstractmethod
    def get_game(self, game_id: str) -> Optional[GameState]:
        pass

    @abstractmethod
    def delete_game(self, game_id: str):
        pass

class InMemoryRepository(GameRepository):
    """
    Simulates a Redis cache using a Python dictionary.
    Crucially, it serializes to JSON to ensure we are testing 
    the same 'boundary logic' that Redis would use.
    """
    def __init__(self):
        self._storage: Dict[str, str] = {}

    def save_game(self, state: GameState):
        # model_dump_json() is the Pydantic v2 way to serialize
        self._storage[state.game_id] = state.model_dump_json()

    def get_game(self, game_id: str) -> Optional[GameState]:
        data = self._storage.get(game_id)
        if not data:
            return None
        # model_validate_json() is the Pydantic v2 way to deserialize
        return GameState.model_validate_json(data)

    def delete_game(self, game_id: str):
        if game_id in self._storage:
            del self._storage[game_id]

# Singleton instance for the app
repository = InMemoryRepository()
