import random
from .base import Agent
from backend.core.schemas import Action

class RandomAgent(Agent):
    name = "random"

    def act(self, observation):
        return Action(move=random.choice(observation.legal_moves) if observation.legal_moves else None)
