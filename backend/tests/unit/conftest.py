import pytest
from app.models.game import City, Route, RouteColor, GoalCard, GameStatus
from app.core.engine import create_initial_state, choose_goals

@pytest.fixture
def mock_cities():
    return {
        "A": City(id="A", name="City A"),
        "B": City(id="B", name="City B"),
        "C": City(id="C", name="City C")
    }

@pytest.fixture
def mock_board():
    board = {
        "r1": Route(id="r1", node_a="A", node_b="B", length=3, color=RouteColor.RED),
        "r2": Route(id="r2", node_a="A", node_b="B", length=3, color=RouteColor.BLUE, sibling_id="r1")
    }
    board["r1"].sibling_id = "r2"
    return board

@pytest.fixture
def mock_goals():
    return [GoalCard(id=f"g{i}", node_a="A", node_b="B", points=5) for i in range(10)]

@pytest.fixture
def game_state(mock_cities, mock_board, mock_goals):
    """Returns a game in SETUP status (initialization done)."""
    return create_initial_state("test_game", ["p1", "p2"], mock_cities, mock_board, mock_goals)


@pytest.fixture
def active_game(game_state):
    """Returns a game in ACTIVE status (goals chosen)."""
    for pid in game_state.players:
        pending = [g.id for g in game_state.players[pid].pending_goals]
        choose_goals(game_state, pid, pending[:2])
    return game_state
