from typing import Optional, Any, Union

from .move import Pass, Move
from .strategy import Strategy
from ..Common.board import Board
from ..Common.position import Position
from ..Common.state import State
from ..Common.utils import Just, Maybe, Nothing


# TODO: implement class

Acknowledgement = Any
ACK_OBJECT = object()


class APIPlayer:
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html.
    """

    __name: str
    __strategy: Strategy
    __goal_position: Maybe[Position]
    __won: Maybe[bool]

    def __init__(self, name: str, strategy: Strategy):
        """
        Creates an instance of an API player with a given name and strategy
        :param name: A string representing the name of this player
        :param strategy: A Strategy representing the strategy of this player
        """
        self.__name = name
        self.__strategy = strategy
        self.__goal_position = Nothing()
        self.__won = Nothing()

    def setup(self, state: Optional[State], goal_position: Position) -> Acknowledgement:
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: an acknowledgment that the message has been received
        """
        self.__goal_position = Just(goal_position)
        return ACK_OBJECT

    @staticmethod
    def propose_board0(rows: int, columns: int) -> Board:
        """
        A method for a player to propose a Board, the player will propose a random Board
        NOTE: We are working under the assumption that a board is still square and will thus create a square board
        of size NxN where N is equal to the maximum of rows and columns
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :return: A Board representing the Board this player proposes
        """
        dimensions = max(rows, columns)
        return Board.from_random_board(dimensions)

    def name(self) -> str:
        """
        Returns the name of this player
        :return: A string representing this player's name
        """
        return self.__name

    def take_turn(self, current_state: State) -> Union[Move, Pass]:
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: A Move or Pass representing the player's selection action on its turn
        """
        goal_pos = self.__goal_position.get_or_throw("take_turn must not be called before setup")
        current_position = current_state.get_active_player_position()
        return self.__strategy.generate_move(current_state, current_position, goal_pos)

    def won(self, did_win: bool) -> Acknowledgement:
        """
        Stores the given outcome of the game
        :param did_win: A boolean
        :return: an acknowledgment that the message has been received
        """
        self.__won = Just(did_win)
        return ACK_OBJECT
