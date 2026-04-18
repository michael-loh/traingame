import pytest
from app.utils.config_loader import load_map_config
from app.core.engine import (
    create_initial_state, choose_goals, draw_train_card, 
    claim_route, draw_goal_cards, calculate_final_scores
)
from app.models.game import GoalCard, GameStatus, TrainCard, TrainColor
from app.persistence.redis_client import InMemoryRepository

def test_full_scripted_playthrough():
    # --- SETUP ---
    repo = InMemoryRepository()
    cities, board = load_map_config("map_config/test_grid.json")
    
    # ... (goals setup same as before)
    goals = [
        GoalCard(id="alice_g1", node_a="0-0", node_b="2-0", points=10),
        GoalCard(id="bob_g1", node_a="0-2", node_b="2-2", points=10),
        GoalCard(id="extra_1", node_a="0-0", node_b="0-2", points=5),
        GoalCard(id="extra_2", node_a="2-0", node_b="2-2", points=5),
        GoalCard(id="extra_3", node_a="1-1", node_b="1-2", points=5),
    ] + [GoalCard(id=f"dummy{i}", node_a="0-0", node_b="1-0", points=1) for i in range(5)]
    
    state = create_initial_state("full-game", ["alice", "bob"], cities, board, goals)
    game_id = state.game_id
    
    # Force state and save to repo
    state.players["alice"].pending_goals = [
        GoalCard(id="alice_g1", node_a="0-0", node_b="2-0", points=10),
        GoalCard(id="extra_1", node_a="0-0", node_b="0-2", points=5),
        GoalCard(id="extra_dummy", node_a="1-1", node_b="1-2", points=1)
    ]
    state.players["bob"].pending_goals = [
        GoalCard(id="bob_g1", node_a="0-2", node_b="2-2", points=10),
        GoalCard(id="extra_2", node_a="2-0", node_b="2-2", points=5),
        GoalCard(id="extra_dummy2", node_a="1-1", node_b="1-2", points=1)
    ]
    state.goal_deck = [
        GoalCard(id="extra_3", node_a="1-1", node_b="1-2", points=5),
        GoalCard(id="d1", node_a="0-0", node_b="1-0", points=1),
        GoalCard(id="d2", node_a="0-0", node_b="1-0", points=1),
    ]
    state.turn_order = ["alice", "bob"]
    state.current_turn_index = 0
    
    repo.save_game(state)

    # --- HELPER FOR TURNS ---
    def sync_and_get():
        nonlocal state
        repo.save_game(state)
        state = repo.get_game(game_id)

    # --- INITIAL GOALS ---
    choose_goals(state, "alice", ["alice_g1", "extra_1"])
    choose_goals(state, "bob", ["bob_g1", "extra_2"])
    sync_and_get()
    assert state.status == GameStatus.ACTIVE

    # --- EARLY GAME: DRAWING ---
    draw_train_card(state, "alice", None)
    sync_and_get()
    draw_train_card(state, "alice", None)
    sync_and_get()
    
    draw_train_card(state, "bob", None)
    sync_and_get()
    draw_train_card(state, "bob", None)
    sync_and_get()

    # --- MID GAME: CLAIMING ---
    state.players["alice"].hand.extend([
        TrainCard(id="a_r1", color=TrainColor.RED),
        TrainCard(id="a_r2", color=TrainColor.RED)
    ])
    claim_route(state, "alice", "r1", ["a_r1", "a_r2"])
    sync_and_get()
    
    state.players["bob"].hand.extend([
        TrainCard(id="b_y1", color=TrainColor.YELLOW),
        TrainCard(id="b_y2", color=TrainColor.YELLOW)
    ])
    claim_route(state, "bob", "r5", ["b_y1", "b_y2"])
    sync_and_get()

    state.players["alice"].hand.extend([
        TrainCard(id="a_b1", color=TrainColor.BLUE),
        TrainCard(id="a_b2", color=TrainColor.BLUE)
    ])
    claim_route(state, "alice", "r2", ["a_b1", "a_b2"])
    sync_and_get()
    assert state.players["alice"].goals[0].id == "alice_g1"
    assert state.players["alice"].goals[0].is_completed == True

    # --- DRAWING MORE GOALS ---
    draw_goal_cards(state, "bob")
    sync_and_get()
    choose_goals(state, "bob", ["extra_3"])
    sync_and_get()

    # --- END GAME TRIGGER ---
    state.players["alice"].train_cars_remaining = 4
    state.players["alice"].hand.extend([
        TrainCard(id="a_w1", color=TrainColor.WHITE),
        TrainCard(id="a_w2", color=TrainColor.WHITE)
    ])
    claim_route(state, "alice", "r7", ["a_w1", "a_w2"])
    sync_and_get()
    
    assert state.status == GameStatus.FINAL_ROUND

    # --- FINAL ROUND ---
    state.players["bob"].hand.extend([
        TrainCard(id="b_bk1", color=TrainColor.BLACK),
        TrainCard(id="b_bk2", color=TrainColor.BLACK)
    ])
    claim_route(state, "bob", "r6", ["b_bk1", "b_bk2"])
    sync_and_get()

    draw_train_card(state, "alice", None)
    sync_and_get()
    draw_train_card(state, "alice", None)
    sync_and_get()

    # --- SCORING ---
    assert state.status == GameStatus.FINISHED
    calculate_final_scores(state)
    sync_and_get()

    assert state.players["alice"].score == 21
    assert state.players["bob"].score == 4

    print("\nScripted playthrough WITH PERSISTENCE passed!")
