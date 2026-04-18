import pytest
from app.core.engine import (
    draw_train_card, choose_goals, 
    claim_route
)
from app.models.game import (
    GameStatus, TrainColor, Route, 
    TrainCard, RouteColor, Player
)

def test_initialization(game_state):
    assert game_state.status == GameStatus.SETUP
    assert len(game_state.players) == 2
    assert len(game_state.face_up_trains) == 5
    for p in game_state.players.values():
        assert len(p.hand) == 4
        assert len(p.pending_goals) == 3

def test_market_wild_restriction(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    
    # Inject a wild into market
    wild_card = TrainCard(id="wild1", color=TrainColor.WILD)
    active_game.face_up_trains[0] = wild_card
    
    # Draw a blind card first
    draw_train_card(active_game, active_id, None)
    
    # Try to draw the face-up wild (should fail)
    with pytest.raises(ValueError, match="Cannot draw face-up Wild as second card"):
        draw_train_card(active_game, active_id, "wild1")

def test_market_first_wild_ends_turn(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    initial_turn_index = active_game.current_turn_index
    
    wild_card = TrainCard(id="wild1", color=TrainColor.WILD)
    active_game.face_up_trains[0] = wild_card
    
    # Draw face-up wild as FIRST card
    draw_train_card(active_game, active_id, "wild1")
    
    # Turn should have ended
    assert active_game.current_turn_index != initial_turn_index
    assert active_game.cards_drawn_this_turn == 0

def test_explicit_claim_validation(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    player = active_game.players[active_id]
    
    # 1. Provide wrong number of cards
    with pytest.raises(ValueError, match="Must provide exactly 3 cards"):
        claim_route(active_game, active_id, "r1", ["c1", "c2"])

    # 2. Provide cards not in hand
    with pytest.raises(ValueError, match="not in player hand"):
        claim_route(active_game, active_id, "r1", ["fake1", "fake2", "fake3"])

    # 3. Provide mismatched colors for colored route
    player.hand = [
        TrainCard(id="red1", color=TrainColor.RED),
        TrainCard(id="blue1", color=TrainColor.BLUE),
        TrainCard(id="wild1", color=TrainColor.WILD)
    ]
    # r1 is RED. blue1 should fail.
    with pytest.raises(ValueError, match="does not match route color red"):
        claim_route(active_game, active_id, "r1", ["red1", "blue1", "wild1"])

def test_grey_route_mixed_color_validation(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    player = active_game.players[active_id]
    
    # Create a grey route
    active_game.board["grey"] = Route(id="grey", node_a="A", node_b="C", length=2, color=RouteColor.ANY)
    
    player.hand = [
        TrainCard(id="red1", color=TrainColor.RED),
        TrainCard(id="blue1", color=TrainColor.BLUE),
    ]
    # Cannot mix Red and Blue on a grey route
    with pytest.raises(ValueError, match="must be of the same color"):
        claim_route(active_game, active_id, "grey", ["red1", "blue1"])

def test_sibling_route_restriction_small_game(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    player = active_game.players[active_id]
    
    player.hand = [TrainCard(id=f"card_{i}", color=TrainColor.RED) for i in range(3)]
    card_ids = [c.id for c in player.hand]
    claim_route(active_game, active_id, "r1", card_ids)
    
    next_id = active_game.turn_order[active_game.current_turn_index]
    p2 = active_game.players[next_id]
    p2.hand = [TrainCard(id=f"card_{i+10}", color=TrainColor.BLUE) for i in range(3)]
    card_ids_p2 = [c.id for c in p2.hand]
    
    with pytest.raises(ValueError, match="Parallel route exclusive"):
        claim_route(active_game, next_id, "r2", card_ids_p2)

def test_final_round_trigger(active_game):
    active_id = active_game.turn_order[active_game.current_turn_index]
    player = active_game.players[active_id]
    
    player.train_cars_remaining = 5
    player.hand = [TrainCard(id=f"card_{i}", color=TrainColor.RED) for i in range(3)]
    card_ids = [c.id for c in player.hand]
    
    claim_route(active_game, active_id, "r1", card_ids)
    
    assert active_game.status == GameStatus.FINAL_ROUND
    assert active_game.final_turns_remaining == 2

def test_deck_reshuffle(active_game):
    active_game.train_deck = []
    active_game.train_discard = [TrainCard(id="old", color=TrainColor.RED)]
    
    active_id = active_game.turn_order[active_game.current_turn_index]
    draw_train_card(active_game, active_id, None)
    
    assert active_game.players[active_id].hand[-1].id == "old"
    assert len(active_game.train_discard) == 0
