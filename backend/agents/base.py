from abc import ABC, abstractmethod
from backend.core.schemas import Observation, Action

class Agent(ABC):
    name: str

    @abstractmethod
    def act(self, observation: Observation) -> Action:
        ...
