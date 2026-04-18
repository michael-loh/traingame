export enum TrainColor {
  RED = "red",
  BLUE = "blue",
  GREEN = "green",
  YELLOW = "yellow",
  BLACK = "black",
  WHITE = "white",
  ORANGE = "orange",
  PINK = "pink",
  WILD = "wild",
}

export enum RouteColor {
  RED = "red",
  BLUE = "blue",
  GREEN = "green",
  YELLOW = "yellow",
  BLACK = "black",
  WHITE = "white",
  ORANGE = "orange",
  PINK = "pink",
  ANY = "any",
}

export enum GameStatus {
  LOBBY = "lobby",
  SETUP = "setup",
  ACTIVE = "active",
  FINAL_ROUND = "final_round",
  FINISHED = "finished",
}

export interface City {
  id: string;
  name: string;
  x: number;
  y: number;
}

export interface Route {
  id: string;
  node_a: string;
  node_b: string;
  length: number;
  color: RouteColor;
  required_wildcards: number;
  owner_id: string | null;
  sibling_id: string | null;
}

export interface TrainCard {
  id: string;
  color: TrainColor;
}

export interface GoalCard {
  id: string;
  node_a: string;
  node_b: string;
  points: number;
  is_completed: boolean;
}

export interface Player {
  player_id: string;
  score: number;
  train_cars_remaining: number;
  hand: TrainCard[];
  goals: GoalCard[];
  pending_goals: GoalCard[];
}

export interface GameState {
  game_id: string;
  status: GameStatus;
  turn_order: string[];
  current_turn_index: number;
  cards_drawn_this_turn: number;
  final_turns_remaining: number;
  cities: Record<string, City>;
  board: Record<string, Route>;
  face_up_trains: TrainCard[];
  players: Record<string, Player>;
  // We don't expose decks to the client in the same way, 
  // but we might need counts if the backend sends them.
  train_deck_count?: number;
  goal_deck_count?: number;
}
