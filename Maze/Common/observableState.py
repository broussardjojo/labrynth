from typing import List, Tuple

from .board import Board
from .direction import Direction


class ObservableState:
    """
    Base class for a State which only exposes information to untrusted users of this class. It does not give access to
    Player information or allow users to change the Board for this State.
    """
    _board: Board
    _previous_moves: List[Tuple[int, Direction]]

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]]):
        """
        A constructor for a State, taking in a Board which represents the board for a game of Labyrinth.
        :param board: a Board representing the board for a game of Labyrinth
        """
        self._board = board
        self._previous_moves = previous_moves

    def get_board(self) -> Board:
        """
        Gets the __board in this State
        :return: a Board representing this State's board
        """
        return self._board

    def get_all_previous_non_passes(self) -> List[Tuple[int, Direction]]:
        """
        Returns a list of all the previous slides and inserts.
        :return: a list of (int, Direction) representing all the previous slides and inserts
        """
        return self._previous_moves
