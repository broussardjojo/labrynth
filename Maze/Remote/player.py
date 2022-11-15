from typing import Union, Optional

from .messenger import Messenger
from ..Common.board import Board
from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..Players.api_player import APIPlayer, Acknowledgement
from ..Players.move import Move, Pass


class RemotePlayer(APIPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html by interacting through a Messenger with a player
    running elsewhere.
    """

    __messenger: Messenger

    def __init__(self, messenger: Messenger):
        self.__messenger = messenger

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: an acknowledgment that the message has been received
        """
        return self.__messenger.call("setup", (state, goal_position))

    def propose_board0(self, rows: int, columns: int) -> Board:
        """
        A method for a player to propose a Board
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :return: A Board representing the Board this player proposes
        """
        return self.__messenger.call("propose_board0", (rows, columns))

    def name(self) -> str:
        """
        Returns the name of this player
        :return: A string representing this player's name
        """
        return self.__messenger.call("name", ())

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: A Move or Pass representing the player's selection action on its turn
        """
        return self.__messenger.call("take_turn", (current_state,))

    def win(self, did_win: bool) -> Acknowledgement:
        """
        Informs this player of the given outcome of the game
        :param did_win: A boolean which is True if the player won (outright or tied), and False otherwise
        :return: an acknowledgment that the message has been received
        """
        return self.__messenger.call("win", (did_win,))
