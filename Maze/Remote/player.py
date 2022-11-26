import logging
import socket
from typing import Union, Optional, Iterator, Any, IO

import ijson

from Maze.Remote.remote_player_methods import RemotePlayerMethods
from Maze.Common.board import Board
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Players.api_player import APIPlayer, Acknowledgement
from Maze.Players.move import Move, Pass

log = logging.getLogger(__name__)


class RemotePlayer(APIPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html by interacting through a Messenger with a player
    running elsewhere.
    """

    __read_channel: Iterator[Any]
    __write_channel: IO[bytes]

    def __init__(self, name: str, read_channel: Iterator[Any], write_channel: IO[bytes]):
        """
        Method to construct a RemotePlayer with a read channel and write channel
        :param name: the player's name
        :param read_channel: a generator of JSON values representing where responses will arrive
        :param write_channel: a BufferedIOBase representing where requests will go
        """
        self.__name = name
        self.__read_channel = read_channel
        self.__write_channel = write_channel

    @classmethod
    def from_socket(cls, name: str, connection: socket.socket) -> "RemotePlayer":
        """
        Method to construct a RemotePlayer given a socket
        :param name: the player's name
        :param connection: a socket.socket connected to a program compatible with the Remote Interactions spec
        :return: A RemotePlayer
        """
        binary_read_channel = connection.makefile("rb", buffering=0)
        read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
        return cls(name, read_channel, connection.makefile("wb", buffering=0))

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: an acknowledgment that the message has been received
        """
        return RemotePlayerMethods.setup.call((state, goal_position), self.__read_channel, self.__write_channel)

    def propose_board0(self, rows: int, columns: int) -> Board:
        """
        A method for a player to propose a Board
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :return: A Board representing the Board this player proposes
        """
        raise RuntimeError("RemotePlayer does not support propose_board0")

    def name(self) -> str:
        """
        Returns the name of this player
        :return: A string representing this player's name
        """
        return self.__name

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: A Move or Pass representing the player's selection action on its turn
        """
        return RemotePlayerMethods.take_turn.call((current_state,), self.__read_channel, self.__write_channel)

    def win(self, did_win: bool) -> Acknowledgement:
        """
        Informs this player of the given outcome of the game
        :param did_win: A boolean which is True if the player won (outright or tied), and False otherwise
        :return: an acknowledgment that the message has been received
        """
        return RemotePlayerMethods.win.call((did_win,), self.__read_channel, self.__write_channel)
