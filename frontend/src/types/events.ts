import { GameState } from "./game";

export enum EventType {
  // Incoming (Client -> Server)
  CHOOSE_GOALS = "CHOOSE_GOALS",
  DRAW_TRAIN_CARD = "DRAW_TRAIN_CARD",
  CLAIM_ROUTE = "CLAIM_ROUTE",
  DRAW_GOAL_CARDS = "DRAW_GOAL_CARDS",

  // Outgoing (Server -> Client)
  GAME_UPDATE = "GAME_UPDATE",
  ERROR = "ERROR",
}

export interface GameEvent {
  type: EventType;
  payload: any;
}

export interface GameUpdatePayload {
  state: GameState;
}

export interface ErrorPayload {
  message: string;
}

export interface ChooseGoalsPayload {
  kept_goal_ids: string[];
}

export interface DrawTrainCardPayload {
  card_id: string | null; // null for blind draw
}

export interface ClaimRoutePayload {
  route_id: string;
  card_ids: string[];
}
