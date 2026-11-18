import asyncio
import chess
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.game_loop import game_loop
from backend.agents.random_agent import RandomAgent
from backend.core.schemas import Action

def test_loop():
    events = []
    async def emit(e):
        events.append(e)
    asyncio.run(game_loop(RandomAgent(), RandomAgent(), emit, max_plies=20))
    assert events[0]["type"] == "game_started"
    assert events[-1]["type"] == "game_over"
    for e in events:
        if e["type"] == "move":
            assert chess.Board(e["fen"]).is_valid()

def test_illegal():
    class Invalid(RandomAgent):
        def act(self, observation):
            return Action(move="a1a8")
    events = []
    async def emit(e):
        events.append(e)
    asyncio.run(game_loop(Invalid(), RandomAgent(), emit, max_plies=1))
    assert events[1]["type"] == "illegal"
    assert events[2]["type"] == "move"

def test_ws():
    with TestClient(app) as client:
        app.state.config["max_plies"] = 2
        app.state.config["move_delay"] = 0
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "start"})
            assert ws.receive_json()["type"] == "game_started"
            assert ws.receive_json()["type"] == "move"
            assert ws.receive_json()["type"] == "move"
            assert ws.receive_json()["type"] == "game_over"
            ws.send_json({"type": "stop"})
            reset = ws.receive_json()
            assert reset["type"] == "game_reset"
            assert chess.Board(reset["fen"]) == chess.Board()
        with client.websocket_connect("/ws") as ws:
            assert ws.receive_json()["type"] == "game_reset"
