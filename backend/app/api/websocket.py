import json
import logging
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.models.events import GameEvent, EventType, ErrorPayload, ChooseGoalsPayload, DrawTrainCardPayload, ClaimRoutePayload
from app.persistence.redis_client import repository
from app.core.engine import choose_goals, draw_train_card, claim_route, draw_goal_cards
from app.core.sanitization import sanitize_state_for_player

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # game_id -> {player_id -> WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # game_id -> asyncio.Lock
        self.locks: Dict[str, asyncio.Lock] = {}

    def get_lock(self, game_id: str) -> asyncio.Lock:
        if game_id not in self.locks:
            self.locks[game_id] = asyncio.Lock()
        return self.locks[game_id]

    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        self.active_connections[game_id][player_id] = websocket
        
        state = repository.get_game(game_id)
        if state:
            await self.send_personal_message(state, game_id, player_id)

    def disconnect(self, game_id: str, player_id: str):
        if game_id in self.active_connections:
            if player_id in self.active_connections[game_id]:
                del self.active_connections[game_id][player_id]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                if game_id in self.locks:
                    del self.locks[game_id]

    async def send_personal_message(self, state, game_id: str, player_id: str):
        ws = self.active_connections.get(game_id, {}).get(player_id)
        if ws:
            sanitized = sanitize_state_for_player(state, player_id)
            await ws.send_json({"type": EventType.GAME_UPDATE, "payload": sanitized})

    async def broadcast_state(self, game_id: str):
        state = repository.get_game(game_id)
        if not state: return
        if game_id in self.active_connections:
            for player_id in self.active_connections[game_id]:
                await self.send_personal_message(state, game_id, player_id)

    async def send_error(self, websocket: WebSocket, message: str):
        await websocket.send_json({
            "type": EventType.ERROR,
            "payload": ErrorPayload(message=message).model_dump()
        })

manager = ConnectionManager()

async def handle_game_event(game_id: str, player_id: str, event: GameEvent):
    # Get the lock for this specific game
    lock = manager.get_lock(game_id)
    
    async with lock:
        state = repository.get_game(game_id)
        if not state:
            logger.error(f"Game {game_id} not found")
            return

        try:
            if event.type == EventType.CHOOSE_GOALS:
                payload = ChooseGoalsPayload(**event.payload)
                choose_goals(state, player_id, payload.kept_goal_ids)
                
            elif event.type == EventType.DRAW_TRAIN_CARD:
                payload = DrawTrainCardPayload(**event.payload)
                draw_train_card(state, player_id, payload.card_id)
                
            elif event.type == EventType.CLAIM_ROUTE:
                payload = ClaimRoutePayload(**event.payload)
                claim_route(state, player_id, payload.route_id, payload.card_ids)
                
            elif event.type == EventType.DRAW_GOAL_CARDS:
                draw_goal_cards(state, player_id)

            repository.save_game(state)
            await manager.broadcast_state(game_id)

        except ValueError as e:
            ws = manager.active_connections.get(game_id, {}).get(player_id)
            if ws: await manager.send_error(ws, str(e))
        except Exception as e:
            logger.exception(f"Unexpected error handling {event.type}")
            ws = manager.active_connections.get(game_id, {}).get(player_id)
            if ws: await manager.send_error(ws, "An internal server error occurred")
