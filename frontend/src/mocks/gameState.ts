import { GameState, GameStatus, TrainColor, RouteColor } from "../types/game";

export const mockGameState: GameState = {
  game_id: "demo-123",
  status: GameStatus.ACTIVE,
  turn_order: ["Alice", "Bob", "Charlie"],
  current_turn_index: 0,
  cards_drawn_this_turn: 0,
  final_turns_remaining: 0,
  cities: {
    "nyc": { id: "nyc", name: "New York", x: 80, y: 30 },
    "bos": { id: "bos", name: "Boston", x: 90, y: 15 },
    "dc": { id: "dc", name: "Washington DC", x: 75, y: 50 },
    "pit": { id: "pit", name: "Pittsburgh", x: 60, y: 35 },
    "buf": { id: "buf", name: "Buffalo", x: 55, y: 20 },
  },
  board: {
    "r1": { id: "r1", node_a: "nyc", node_b: "bos", length: 2, color: RouteColor.RED, required_wildcards: 0, owner_id: null, sibling_id: null },
    "r2": { id: "r2", node_a: "nyc", node_b: "dc", length: 2, color: RouteColor.WHITE, required_wildcards: 0, owner_id: "Alice", sibling_id: null },
    "r3": { id: "r3", node_a: "nyc", node_b: "pit", length: 3, color: RouteColor.ANY, required_wildcards: 0, owner_id: null, sibling_id: "r4" },
    "r4": { id: "r4", node_a: "nyc", node_b: "pit", length: 3, color: RouteColor.ANY, required_wildcards: 0, owner_id: null, sibling_id: "r3" },
    "r5": { id: "r5", node_a: "bos", node_b: "buf", length: 3, color: RouteColor.BLUE, required_wildcards: 0, owner_id: null, sibling_id: null },
    "r6": { id: "r6", node_a: "pit", node_b: "buf", length: 2, color: RouteColor.YELLOW, required_wildcards: 0, owner_id: "Bob", sibling_id: null },
  },
  face_up_trains: [
    { id: "c1", color: TrainColor.RED },
    { id: "c2", color: TrainColor.BLUE },
    { id: "c3", color: TrainColor.GREEN },
    { id: "c4", color: TrainColor.WILD },
    { id: "c5", color: TrainColor.PINK },
  ],
  players: {
    "Alice": {
      player_id: "Alice",
      score: 45,
      train_cars_remaining: 32,
      hand: [
        { id: "h1", color: TrainColor.RED },
        { id: "h2", color: TrainColor.RED },
        { id: "h3", color: TrainColor.BLUE },
        { id: "h4", color: TrainColor.WILD },
        { id: "h5", color: TrainColor.GREEN },
        { id: "h6", color: TrainColor.GREEN },
      ],
      goals: [
        { id: "g1", node_a: "New York", node_b: "Washington DC", points: 8, is_completed: true },
        { id: "g2", node_a: "Boston", node_b: "Pittsburgh", points: 12, is_completed: false },
      ],
      pending_goals: [],
    },
    "Bob": {
      player_id: "Bob",
      score: 22,
      train_cars_remaining: 30,
      hand: Array(5).fill({ id: "mock", color: TrainColor.RED }), // Minimized for HUD
      goals: [],
      pending_goals: [],
    },
    "Charlie": {
      player_id: "Charlie",
      score: 10,
      train_cars_remaining: 45,
      hand: Array(12).fill({ id: "mock", color: TrainColor.RED }),
      goals: [],
      pending_goals: [],
    }
  },
  train_deck_count: 82,
  goal_deck_count: 24,
};
