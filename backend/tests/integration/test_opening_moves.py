import pytest
from app.utils.config_loader import load_map_config
from app.core.engine import create_initial_state, choose_goals, draw_train_card, claim_route
from app.models.game import GoalCard, GameStatus, TrainCard, TrainColor

def test_simulated_game_on_grid():
    # 1. Load the real test map
    cities, board = load_map_config("map_config/test_grid.json")
    
    # 2. Setup mock goals
    goals = [
        GoalCard(id="g1", node_a="0-0", node_b="2-2", points=20),
        GoalCard(id="g2", node_a="0-2", node_b="2-0", points=20),
        GoalCard(id="g3", node_a="0-0", node_b="0-2", points=5),
        GoalCard(id="g4", node_a="2-0", node_b="2-2", points=5),
        GoalCard(id="g5", node_a="1-1", node_b="0-0", points=10),
        GoalCard(id="g6", node_a="1-1", node_b="2-2", points=10),
    ]
    
    # 3. Initialize Game
    state = create_initial_state("integration-test", ["alice", "bob"], cities, board, goals)
    assert state.status == GameStatus.SETUP
    
    # Verify siblings were wired correctly by the loader
    assert state.board["r4_a"].sibling_id == "r4_b"
    assert state.board["r4_b"].sibling_id == "r4_a"

    # 4. Choose Initial Goals
    for pid in ["alice", "bob"]:
        pending = [g.id for g in state.players[pid].pending_goals]
        choose_goals(state, pid, pending[:2])
    
    assert state.status == GameStatus.ACTIVE

    # 5. Play Turns
    # Alice's Turn - Draw two cards
    alice_id = state.turn_order[state.current_turn_index]
    draw_train_card(state, alice_id, None) # Blind
    draw_train_card(state, alice_id, state.face_up_trains[0].id) # Market
    
    assert len(state.players[alice_id].hand) == 6
    assert state.current_turn_index == 1 # Move to Bob
    
    # Bob's Turn - Claim a route
    bob_id = state.turn_order[state.current_turn_index]
    p_bob = state.players[bob_id]
    
    # Give 'Bob' 2 Red cards manually to claim r1 (0-0 to 1-0)
    p_bob.hand = [
        TrainCard(id="red1", color=TrainColor.RED),
        TrainCard(id="red2", color=TrainColor.RED)
    ]
    
    claim_route(state, bob_id, "r1", ["red1", "red2"])
    
    assert state.board["r1"].owner_id == bob_id
    assert p_bob.score == 2 # 2-length route = 2 points
    assert p_bob.train_cars_remaining == 43
    
    # 6. Verify Double Route Constraint on Grid
    # Alice tries to claim r4_b (sibling of r4_a) in a 2-player game
    # First, Bob claims r4_a
    alice_id = state.turn_order[state.current_turn_index] # Should be alice again
    # Give alice cards for r4_b
    p_alice = state.players[alice_id]
    p_alice.hand = [TrainCard(id="o1", color=TrainColor.ORANGE), TrainCard(id="o2", color=TrainColor.ORANGE)]
    
    # Bob takes r4_a (cheat a bit to test the constraint)
    state.board["r4_a"].owner_id = "bob"
    
    with pytest.raises(ValueError, match="Parallel route exclusive"):
        claim_route(state, alice_id, "r4_b", ["o1", "o2"])

    print("\nIntegration test on 3x3 grid passed successfully!")
