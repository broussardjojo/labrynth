from abc import ABC, abstractmethod

from ..Common.state import ObservableState
from ..Common.position import Position
from .move import Move


class Strategy(ABC):
    @abstractmethod
    def generate_move(self, current_state: ObservableState,
                      current_position: Position,
                      target_position: Position) -> Move:
        pass
