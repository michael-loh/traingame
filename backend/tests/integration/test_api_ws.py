import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.events import EventType

def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_lobby_to_game_flow():
    client = TestClient(app)
    
    # 1. Create Game (Empty Lobby)
    response = client.post("/games")
    assert response.status_code == 200
    game_id = response.json()["game_id"]
    
    # 2. Join Alice
    resp_alice = client.post(f"/games/{game_id}/join", json={"player_id": "alice"})
    alice_token = resp_alice.json()["secret_token"]
    
    # 3. Join Bob
    client.post(f"/games/{game_id}/join", json={"player_id": "bob"})
    
    # 4. Connect Alice via WebSocket (with token)
    with client.websocket_connect(f"/ws/{game_id}/alice?token={alice_token}") as alice_ws:
        # Should receive initial sanitized state (status: LOBBY)
        data = alice_ws.receive_json()
        assert data["type"] == EventType.GAME_UPDATE
        assert data["payload"]["status"] == "lobby"
        
        # 5. Start Game
        start_resp = client.post(f"/games/{game_id}/start")
        assert start_resp.status_code == 200
        
        # Alice should receive a broadcast update (status: SETUP)
        data = alice_ws.receive_json()
        assert data["type"] == EventType.GAME_UPDATE
        assert data["payload"]["status"] == "setup"
        # 6. Action: Alice chooses goals
        pending_ids = [g["id"] for g in data["payload"]["players"]["alice"]["pending_goals"]]
        alice_ws.send_json({
            "type": EventType.CHOOSE_GOALS,
            "payload": {"kept_goal_ids": pending_ids[:2]}
        })
        
        # Alice gets update
        data = alice_ws.receive_json()
        assert data["type"] == EventType.GAME_UPDATE
        assert len(data["payload"]["players"]["alice"]["goals"]) == 2

def test_invalid_connection():
    client = TestClient(app)
    # Non-existent game (providing a token so it passes FastAPI validation)
    with client.websocket_connect("/ws/fake-game/alice?token=dummy") as ws:
        data = ws.receive_json()
        assert data["type"] == "ERROR"
        assert "Game not found" in data["payload"]["message"]

def test_unauthorized_token():
    client = TestClient(app)
    # 1. Create Game
    response = client.post("/games")
    game_id = response.json()["game_id"]
    client.post(f"/games/{game_id}/join", json={"player_id": "alice"})
    
    # 2. Try to connect with WRONG token
    with client.websocket_connect(f"/ws/{game_id}/alice?token=wrong-token") as ws:
        data = ws.receive_json()
        assert data["type"] == "ERROR"
        assert "Unauthorized" in data["payload"]["message"]
