from typing import List, Tuple

from .board import Board
from .direction import Direction


class ObservableState:
    """
    Base class for a State which only exposes information to untrusted users of this class. It does not give access to
    Player information or allow users to change the Board for this State.
    """

    def __init__(self, board: Board, previous_moves):
        """
        A constructor for a State, taking in a Board which represents the board for a game of Labyrinth.
        :param board: a Board representing the board for a game of Labyrinth
        """
        self.__board = board
        self.__previous_moves = previous_moves

    def get_board(self) -> Board:
        """
        Gets the __board in this State
        :return: a Board representing this State's board
        """
        return self.__board

    def get_all_previous_non_passes(self) -> List[Tuple[int, Direction]]:
        """
        Returns a list of all the previous slides and inserts.
        :return: a list of (int, Direction) representing all the previous slides and inserts
        """
        return self.__previous_moves
