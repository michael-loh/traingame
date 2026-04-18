from typing import List
from app.models.game import GoalCard

def get_test_goals() -> List[List[GoalCard]]:
    """
    Returns a standardized set of goals for the 3x3 test grid.
    In a real app, these would be loaded from a JSON file like the map.
    """
    return [
        GoalCard(id="g1", node_a="0-0", node_b="2-2", points=20),
        GoalCard(id="g2", node_a="0-2", node_b="2-0", points=20),
        GoalCard(id="g3", node_a="0-0", node_b="0-2", points=8),
        GoalCard(id="g4", node_a="2-0", node_b="2-2", points=8),
        GoalCard(id="g5", node_a="1-1", node_b="0-0", points=10),
        GoalCard(id="g6", node_a="1-1", node_b="2-2", points=10),
        GoalCard(id="g7", node_a="0-1", node_b="2-1", points=12),
        GoalCard(id="g8", node_a="1-0", node_b="1-2", points=12),
        GoalCard(id="g9", node_a="0-2", node_b="1-0", points=15),
        GoalCard(id="g10", node_a="2-0", node_b="0-1", points=15),
    ]
