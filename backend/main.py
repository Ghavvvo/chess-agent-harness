import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.agents.random_agent import RandomAgent
from backend.agents.llm_agent import LLMAgent
from backend.core.game_loop import game_loop
from backend.core.env import ChessEnv
from backend.ws.manager import ConnectionManager

@asynccontextmanager
async def lifespan(app):
    app.state.manager = ConnectionManager()
    app.state.task = None
    app.state.gate = asyncio.Event()
    app.state.gate.set()
    app.state.config = yaml.safe_load((Path(__file__).resolve().parents[1] / "configs/game.yaml").read_text())
    yield
    if app.state.task:
        app.state.task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.task

app = FastAPI(lifespan=lifespan)

def agent(config):
    config = dict(config)
    kind = config.pop("type")
    if kind == "random":
        return RandomAgent()
    if kind == "llm":
        return LLMAgent(**config)
    raise ValueError(f"Unknown agent: {kind}")

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    manager = app.state.manager
    await manager.connect(ws)
    async def run():
            try:
                c = app.state.config
                await game_loop(agent(c["white"]), agent(c["black"]), manager.broadcast,
                    c.get("max_plies", 200), c.get("illegal_fallback", True), c.get("move_delay", .4), app.state.gate.wait)
            except Exception:
                await manager.broadcast({"type": "game_over", "result": "*", "reason": "configuration_error"})
    try:
        while True:
            try:
                command = await ws.receive_json()
            except ValueError:
                continue
            if not isinstance(command, dict):
                continue
            kind = command.get("type")
            if kind == "start" and (app.state.task is None or app.state.task.done()):
                manager.events.clear()
                app.state.gate.set()
                app.state.task = asyncio.create_task(run())
            elif kind in ("pause", "resume") and app.state.task and not app.state.task.done():
                if kind == "pause":
                    app.state.gate.clear()
                else:
                    app.state.gate.set()
                await manager.broadcast({"type": "control", "state": "paused" if kind == "pause" else "running"})
            elif kind == "stop":
                if app.state.task and not app.state.task.done():
                    app.state.task.cancel()
                    with suppress(asyncio.CancelledError):
                        await app.state.task
                app.state.task = None
                app.state.gate.set()
                manager.events.clear()
                await manager.broadcast({"type": "game_reset", "fen": ChessEnv().fen()})
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
