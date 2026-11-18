import chess
from .schemas import Observation

class ChessEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = chess.Board()

    def fen(self):
        return self.board.fen()

    def legal_moves(self):
        return [m.uci() for m in self.board.legal_moves]

    def is_game_over(self):
        return self.board.is_game_over(claim_draw=True)

    def observe(self):
        return Observation(fen=self.fen(), legal_moves=self.legal_moves(),
            side_to_move="white" if self.board.turn else "black",
            ply=len(self.board.move_stack),
            last_move=self.board.peek().uci() if self.board.move_stack else None)

    def step(self, move_uci):
        if move_uci not in self.legal_moves():
            return "illegal"
        self.board.push_uci(move_uci)
        if self.board.is_checkmate():
            return "checkmate"
        if self.board.is_stalemate():
            return "stalemate"
        return "draw" if self.is_game_over() else "ok"
