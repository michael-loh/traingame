import uuid
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from pydantic import BaseModel
from app.models.game import GameState, GameStatus
from app.models.events import GameEvent
from app.core.engine import create_lobby_state, add_player_to_lobby, start_game
from app.utils.config_loader import load_map_config
from app.utils.goal_loader import get_test_goals
from app.persistence.redis_client import repository
from app.api.websocket import manager, handle_game_event

app = FastAPI(title="The Train Game API")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JoinGameRequest(BaseModel):
    player_id: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/games")
def create_game():
    game_id = str(uuid.uuid4())[:8]
    cities, board = load_map_config("map_config/test_grid.json")
    state = create_lobby_state(game_id, cities, board)
    repository.save_game(state)
    return {"game_id": game_id}

@app.post("/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    state = repository.get_game(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        token = add_player_to_lobby(state, request.player_id)
        repository.save_game(state)
        await manager.broadcast_state(game_id)
        return {"status": "joined", "player_id": request.player_id, "secret_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/games/{game_id}/start")
async def trigger_start_game(game_id: str):
    state = repository.get_game(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        goals = get_test_goals()
        start_game(state, goals)
        repository.save_game(state)
        await manager.broadcast_state(game_id)
        return {"status": "started"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str, token: str = Query(...)):
    state = repository.get_game(game_id)
    if not state:
        await websocket.accept()
        await websocket.send_json({"type": "ERROR", "payload": {"message": "Game not found"}})
        await websocket.close()
        return

    # REJOIN LOGIC: Verify secret token
    player = state.players.get(player_id)
    if not player or player.secret_token != token:
        await websocket.accept()
        await websocket.send_json({"type": "ERROR", "payload": {"message": "Unauthorized: Invalid token"}})
        await websocket.close()
        return

    await manager.connect(websocket, game_id, player_id)

    try:
        while True:
            data = await websocket.receive_json()
            event = GameEvent(**data)
            await handle_game_event(game_id, player_id, event)
    except WebSocketDisconnect:
        manager.disconnect(game_id, player_id)
    except Exception:
        manager.disconnect(game_id, player_id)
