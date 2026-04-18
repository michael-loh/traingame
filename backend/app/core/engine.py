import random
import uuid
from typing import List, Dict, Optional
from app.models.game import (
    GameState, Player, TrainCard, GoalCard, 
    TrainColor, RouteColor, GameStatus, City, Route
)
from app.core.constants import (
    TOTAL_COLOR_CARDS, TOTAL_WILD_CARDS, 
    INITIAL_HAND_SIZE, MARKET_SIZE, MAX_MARKET_WILDS,
    INITIAL_TRAIN_CARS, ROUTE_SCORE_TABLE, LONGEST_PATH_BONUS,
    MIN_DRAWN_GOALS, MIN_INITIAL_GOALS
)
from app.core.graph import is_connected, get_longest_path

def create_lobby_state(
    game_id: str, 
    cities: Dict[str, City], 
    board: Dict[str, Route]
) -> GameState:
    """Initializes an empty game lobby."""
    return GameState(
        game_id=game_id,
        status=GameStatus.LOBBY,
        cities=cities,
        board=board,
        players={}
    )

def add_player_to_lobby(state: GameState, player_id: str) -> str:
    """Adds a player to the lobby and returns their secret_token."""
    if state.status != GameStatus.LOBBY:
        raise ValueError("Cannot join game: already started or finished")
    if player_id in state.players:
        raise ValueError("Player already in lobby")
    if len(state.players) >= 5:
        raise ValueError("Lobby is full (max 5 players)")
    
    token = str(uuid.uuid4())
    state.players[player_id] = Player(
        player_id=player_id,
        secret_token=token,
        train_cars_remaining=INITIAL_TRAIN_CARS
    )
    state.turn_order.append(player_id)
    return token

def start_game(state: GameState, goal_cards: List[GoalCard]) -> GameState:
    """
    Shuffles decks, deals starting cards/goals, and moves to SETUP.
    """
    if state.status != GameStatus.LOBBY:
        raise ValueError("Game has already started")
    if len(state.players) < 2:
        raise ValueError("Need at least 2 players to start")

    # 1. Setup Train Deck
    train_deck = []
    for color in TrainColor:
        count = TOTAL_WILD_CARDS if color == TrainColor.WILD else TOTAL_COLOR_CARDS
        for _ in range(count):
            train_deck.append(TrainCard(id=str(uuid.uuid4()), color=color))
    
    random.shuffle(train_deck)
    random.shuffle(goal_cards)
    state.train_deck = train_deck
    state.goal_deck = goal_cards

    # 2. Shuffle Turn Order
    random.shuffle(state.turn_order)

    # 3. Deal Initial Hands
    for player in state.players.values():
        player.hand = [state.train_deck.pop() for _ in range(INITIAL_HAND_SIZE)]
        # Deal initial 3 goal choices
        player.pending_goals = [state.goal_deck.pop() for _ in range(3)]

    # 4. Setup Market
    face_up = []
    while len(face_up) < MARKET_SIZE:
        face_up.append(state.train_deck.pop())
        if sum(1 for c in face_up if c.color == TrainColor.WILD) >= MAX_MARKET_WILDS:
            face_up = [] # Flush and retry
    state.face_up_trains = face_up

    state.status = GameStatus.SETUP
    return state

# --- Legacy Helper for Tests (Updated to use new flow) ---
def create_initial_state(
    game_id: str, 
    player_ids: List[str], 
    cities: Dict[str, City], 
    board: Dict[str, Route],
    goal_cards: List[GoalCard]
) -> GameState:
    state = create_lobby_state(game_id, cities, board)
    for pid in player_ids:
        add_player_to_lobby(state, pid)
    return start_game(state, goal_cards)

def validate_turn(state: GameState, player_id: str):
    if state.status not in [GameStatus.ACTIVE, GameStatus.FINAL_ROUND]:
        raise ValueError("Game is not currently active")
    active_player_id = state.turn_order[state.current_turn_index]
    if active_player_id != player_id:
        raise ValueError(f"It is not {player_id}'s turn")

def reshuffle_discard(state: GameState):
    if not state.train_discard: return
    state.train_deck.extend(state.train_discard)
    state.train_discard = []
    random.shuffle(state.train_deck)

def draw_train_card(state: GameState, player_id: str, card_id: Optional[str] = None) -> GameState:
    validate_turn(state, player_id)
    player = state.players[player_id]
    drawn_card: Optional[TrainCard] = None
    is_wild = False

    if card_id is None:
        if not state.train_deck: reshuffle_discard(state)
        if not state.train_deck: raise ValueError("No cards left")
        drawn_card = state.train_deck.pop()
    else:
        market_idx = next((i for i, c in enumerate(state.face_up_trains) if c.id == card_id), None)
        if market_idx is None: raise ValueError("Card not in market")
        drawn_card = state.face_up_trains.pop(market_idx)
        is_wild = drawn_card.color == TrainColor.WILD
        if is_wild and state.cards_drawn_this_turn > 0:
            state.face_up_trains.insert(market_idx, drawn_card)
            raise ValueError("Cannot draw face-up Wild as second card")
        if not state.train_deck: reshuffle_discard(state)
        if state.train_deck: state.face_up_trains.append(state.train_deck.pop())
        while sum(1 for c in state.face_up_trains if c.color == TrainColor.WILD) >= MAX_MARKET_WILDS:
            state.train_discard.extend(state.face_up_trains)
            state.face_up_trains = []
            for _ in range(MARKET_SIZE):
                if not state.train_deck: reshuffle_discard(state)
                if state.train_deck: state.face_up_trains.append(state.train_deck.pop())

    player.hand.append(drawn_card)
    state.cards_drawn_this_turn += 1
    if state.cards_drawn_this_turn >= 2 or (is_wild and state.cards_drawn_this_turn == 1 and card_id is not None):
        end_turn(state)
    return state

def claim_route(state: GameState, player_id: str, route_id: str, card_ids: List[str]) -> GameState:
    validate_turn(state, player_id)
    if state.cards_drawn_this_turn > 0: raise ValueError("Cannot claim route after drawing")
    
    route = state.board.get(route_id)
    if not route or route.owner_id: raise ValueError("Route unavailable")
    
    if len(state.players) <= 3 and route.sibling_id and state.board[route.sibling_id].owner_id:
        raise ValueError("Parallel route exclusive in small games")
    if route.sibling_id and state.board[route.sibling_id].owner_id == player_id:
        raise ValueError("Cannot own both sides of double route")

    player = state.players[player_id]
    if player.train_cars_remaining < route.length: raise ValueError("Not enough cars")

    if len(card_ids) != route.length:
        raise ValueError(f"Must provide exactly {route.length} cards")

    spent_cards: List[TrainCard] = []
    hand_map = {c.id: c for c in player.hand}
    for cid in card_ids:
        if cid not in hand_map:
            raise ValueError(f"Card {cid} not in player hand")
        spent_cards.append(hand_map.pop(cid))

    required_color = route.color.value if route.color != RouteColor.ANY else None
    chosen_color = None
    for card in spent_cards:
        if card.color == TrainColor.WILD:
            continue
        if required_color and card.color.value != required_color:
            raise ValueError(f"Card {card.id} does not match route color {required_color}")
        if not required_color:
            if chosen_color is None: chosen_color = card.color.value
            elif card.color.value != chosen_color:
                raise ValueError("All cards for a grey route must be of the same color (or Wild)")

    for card in spent_cards:
        player.hand.remove(card)
        state.train_discard.append(card)

    route.owner_id = player_id
    player.train_cars_remaining -= route.length
    player.score += ROUTE_SCORE_TABLE.get(route.length, 0)

    for goal in player.goals:
        if not goal.is_completed:
            if is_connected(player_id, goal.node_a, goal.node_b, state.board):
                goal.is_completed = True
    end_turn(state)
    return state

def draw_goal_cards(state: GameState, player_id: str) -> GameState:
    validate_turn(state, player_id)
    if state.cards_drawn_this_turn > 0: raise ValueError("Cannot draw goals after drawing train cards")
    player = state.players[player_id]
    if player.pending_goals: raise ValueError("Player already has pending goals")
    drawn = [state.goal_deck.pop(0) for _ in range(min(3, len(state.goal_deck)))]
    player.pending_goals = drawn
    return state

def choose_goals(state: GameState, player_id: str, kept_ids: List[str]) -> GameState:
    player = state.players[player_id]
    if not player.pending_goals: raise ValueError("No pending goals")
    min_to_keep = MIN_INITIAL_GOALS if state.status == GameStatus.SETUP else MIN_DRAWN_GOALS
    if len(kept_ids) < min_to_keep: raise ValueError(f"Must keep {min_to_keep}")
    to_keep = [g for g in player.pending_goals if g.id in kept_ids]
    to_discard = [g for g in player.pending_goals if g.id not in kept_ids]
    if len(to_keep) != len(kept_ids): raise ValueError("Invalid goal IDs")
    player.goals.extend(to_keep)
    player.pending_goals = []
    for goal in to_keep:
        if is_connected(player_id, goal.node_a, goal.node_b, state.board): goal.is_completed = True
    state.goal_deck.extend(to_discard)
    if state.status == GameStatus.SETUP:
        if all(not p.pending_goals for p in state.players.values()): state.status = GameStatus.ACTIVE
    else:
        end_turn(state)
    return state

def calculate_final_scores(state: GameState):
    if state.status != GameStatus.FINISHED: raise ValueError("Game not finished")
    for player in state.players.values():
        for goal in player.goals:
            player.score += goal.points if goal.is_completed else -goal.points
    path_lengths = {pid: get_longest_path(pid, state.board) for pid in state.players}
    if path_lengths:
        max_len = max(path_lengths.values())
        if max_len > 0:
            for pid in [p for p, l in path_lengths.items() if l == max_len]:
                state.players[pid].score += LONGEST_PATH_BONUS

def end_turn(state: GameState):
    state.cards_drawn_this_turn = 0
    current_player = state.players[state.turn_order[state.current_turn_index]]
    if state.status == GameStatus.ACTIVE and current_player.train_cars_remaining <= 2:
        state.status = GameStatus.FINAL_ROUND
        state.final_turns_remaining = len(state.turn_order)
    elif state.status == GameStatus.FINAL_ROUND:
        state.final_turns_remaining -= 1
        if state.final_turns_remaining <= 0:
            state.status = GameStatus.FINISHED
            return
    state.current_turn_index = (state.current_turn_index + 1) % len(state.turn_order)
