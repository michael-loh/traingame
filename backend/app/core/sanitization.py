from app.models.game import GameState, Player, GoalCard
from typing import Dict, Any

def sanitize_state_for_player(state: GameState, player_id: str) -> Dict[str, Any]:
    """
    Hides sensitive information (opponent hands, deck contents) before broadcasting.
    """
    # 1. Convert the entire state to a dict
    full_data = state.model_dump()

    # 2. Hide Decks (Only reveal counts)
    full_data["train_deck_count"] = len(full_data.pop("train_deck"))
    full_data["goal_deck_count"] = len(full_data.pop("goal_deck"))
    
    # Keep train_discard visible (it's public knowledge)
    
    # 3. Sanitize Players
    sanitized_players = {}
    for pid, p_data in full_data["players"].items():
        if pid == player_id:
            # Current player sees everything in their own object
            sanitized_players[pid] = p_data
        else:
            # Opponent view: hide hand and goals
            opponent = p_data.copy()
            opponent["hand_count"] = len(opponent.pop("hand"))
            
            # For goals, only show COMPLETED goals? 
            # In TTR, goals are usually hidden until the end.
            # We will show only completed goals to opponents if desired, 
            # but usually they are 100% secret. Let's make them 100% secret.
            opponent["goal_count"] = len(opponent.pop("goals"))
            opponent.pop("pending_goals") # Always secret
            sanitized_players[pid] = opponent
            
    full_data["players"] = sanitized_players

    return full_data
