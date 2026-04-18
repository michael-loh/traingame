import pytest
from app.utils.config_loader import load_map_config
from app.core.engine import (
    create_initial_state, choose_goals, claim_route, calculate_final_scores, draw_train_card
)
from app.models.game import GoalCard, GameStatus, TrainCard, TrainColor

def test_endgame_trigger_and_scoring():
    # 1. Setup
    cities, board = load_map_config("map_config/test_grid.json")
    
    # Enough goals for 2 players (3 each + some extras)
    goals = [GoalCard(id=f"g{i}", node_a="0-0", node_b="1-0", points=10) for i in range(10)]
    
    state = create_initial_state("endgame-test", ["p1", "p2"], cities, board, goals)
    
    # Players keep 2 goals each
    for pid in state.turn_order:
        pending_ids = [g.id for g in state.players[pid].pending_goals]
        choose_goals(state, pid, pending_ids[:2])
    
    assert state.status == GameStatus.ACTIVE

    # 2. Trigger Final Round
    active_id = state.turn_order[state.current_turn_index]
    other_id = state.turn_order[(state.current_turn_index + 1) % 2]
    
    p_active = state.players[active_id]
    p_active.hand = [TrainCard(id="red1", color=TrainColor.RED), TrainCard(id="red2", color=TrainColor.RED)]
    p_active.train_cars_remaining = 4 
    
    # Active player claims r1 (length 2). Remaining cars will be 2 (Trigger point!).
    claim_route(state, active_id, "r1", ["red1", "red2"])
    
    assert state.status == GameStatus.FINAL_ROUND
    assert state.final_turns_remaining == 2 

    # 3. Final Turns
    # Other player's turn
    draw_train_card(state, other_id, None)
    draw_train_card(state, other_id, None)
    
    # Active player's last turn
    draw_train_card(state, active_id, None)
    draw_train_card(state, active_id, None)
    
    # 4. Verify Finished State
    assert state.status == GameStatus.FINISHED
    
    # 5. Calculate and Verify Scores
    calculate_final_scores(state)
    
    # Calculate Expected Active Player Score:
    # Routes: 2 points (r1)
    # Goals: They have 2 goals. r1 connects 0-0 to 1-0. All our mock goals are 0-0 to 1-0.
    # So both goals should be completed (+20 points).
    # Longest Path: They have the only route (+10 points).
    # Total: 2 + 20 + 10 = 32.
    assert state.players[active_id].score == 32
    
    # Calculate Expected Other Player Score:
    # Routes: 0
    # Goals: 2 goals, both failed (-20 points).
    # Total: -20.
    assert state.players[other_id].score == -20

    print("\nEndgame integration test passed successfully!")
