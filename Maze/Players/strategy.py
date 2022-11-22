from abc import ABC, abstractmethod
from typing import Union

from ..Common.abstract_state import AbstractState
from ..Common.position import Position
from .move import Move, Pass


class Strategy(ABC):
    """
    A Strategy which represents a decision system to determine a Move. A strategy is an abstract class which could be
    implemented in any number of ways depending on the Player's AI of choice
    """
    @abstractmethod
    def generate_move(self, current_state: AbstractState, target_position: Position) -> Union[Move, Pass]:
        """
        A method to generate a move selected by the implemented strategy
        :param current_state: An ObservableState representing the current state of the game
        NOTE: the ObservableState provides access to a reference to the board due to Python's pass by reference
        therefore it is important for users to copy the board before making changes to air on the side of caution
        :param target_position: The target Position of the Player (where the goal/home is depending on implementation)
        :return: A Move representing a Slide/Insert, rotate, and destination or a Pass
        """
