import pytest
from app.persistence.redis_client import InMemoryRepository
from app.models.game import GameState, GameStatus

def test_in_memory_persistence(active_game):
    repo = InMemoryRepository()
    game_id = active_game.game_id
    
    # 1. Save
    repo.save_game(active_game)
    
    # 2. Retrieve
    retrieved = repo.get_game(game_id)
    
    assert retrieved is not None
    assert retrieved.game_id == game_id
    assert retrieved.status == GameStatus.ACTIVE
    assert len(retrieved.players) == len(active_game.players)
    
    # 3. Verify it's a deep copy (due to JSON serialization)
    retrieved.status = GameStatus.FINISHED
    assert repo.get_game(game_id).status == GameStatus.ACTIVE
    
    # 4. Delete
    repo.delete_game(game_id)
    assert repo.get_game(game_id) is None

def test_get_nonexistent_game():
    repo = InMemoryRepository()
    assert repo.get_game("fake-id") is None
