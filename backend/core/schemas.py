from typing import Literal
from pydantic import BaseModel

class Observation(BaseModel):
    fen: str
    legal_moves: list[str]
    side_to_move: Literal["white", "black"]
    ply: int
    last_move: str | None

class Action(BaseModel):
    move: str | None
