from abc import ABC, abstractmethod
from state import ObservableState
from position import Position


class Strategy(ABC):
    @abstractmethod
    def generate_slide(self, current_state: ObservableState, current_position: Position, target_position: Position):
        pass

    @abstractmethod
    def generate_rotate(self, current_state: ObservableState, current_position: Position, target_position: Position):
        pass

    @abstractmethod
    def generate_player_move(self, current_state: ObservableState, current_position: Position, target_position: Position):
        pass

    def generate_move(self, current_state: ObservableState, current_position: Position, target_position: Position):
        return Move(self.generate_slide(current_state, current_position, target_position),
                    self.generate_rotate(current_state, current_position, target_position),
                    self.generate_player_move(current_state, current_position, target_position))
