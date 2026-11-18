import asyncio
import json
import random
from .env import ChessEnv

async def game_loop(white, black, emit, max_plies=200, illegal_fallback=True, move_delay=0, wait_for_turn=None):
    env = ChessEnv()
    await emit({"type": "game_started", "white": white.name, "black": black.name, "fen": env.fen()})
    reason = "max_plies"
    for _ in range(max_plies):
        if wait_for_turn is not None:
            await wait_for_turn()
        if env.is_game_over():
            break
        obs = env.observe()
        try:
            action = await asyncio.to_thread((white if obs.side_to_move == "white" else black).act, obs)
            move = action.move
        except Exception:
            await emit({"type": "agent_error", "side": obs.side_to_move, "message": "Agent request failed"})
            reason = "agent_error"
            break
        status = env.step(move)
        if status == "illegal":
            fallback = random.choice(obs.legal_moves) if illegal_fallback else None
            await emit({"type": "illegal", "ply": obs.ply + 1, "attempted": move, "fallback": fallback})
            if fallback is None:
                reason = "illegal_move"
                break
            move = fallback
            status = env.step(move)
        await emit({"type": "move", "ply": obs.ply + 1, "fen": env.fen(), "move_uci": move, "side": obs.side_to_move})
        if env.is_game_over():
            reason = status
            break
        await asyncio.sleep(move_delay)
    await emit({"type": "game_over", "result": env.board.result(claim_draw=True), "reason": reason})

if __name__ == "__main__":
    from backend.agents.random_agent import RandomAgent
    async def output(event):
        print(json.dumps(event))
    asyncio.run(game_loop(RandomAgent(), RandomAgent(), output))
