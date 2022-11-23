from concurrent.futures import Future, ThreadPoolExecutor, Executor
from typing import Any, Optional, Union

from Maze.Common.board import Board
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Players.api_player import APIPlayer
from Maze.Players.move import Move, Pass


class SafeAPIPlayer:
    """
    A class that represents a client of the referee, but always returns a `Future` instead of the direct
    result. This is designed to be used in combination with `gather_protected` and `await_protected`
    """

    player: APIPlayer
    __executor: Executor

    def __init__(self, player: APIPlayer, executor: Executor):
        """
        Creates a SafeAPIPlayer which wraps a given APIPlayer by executing its methods in an executor
        :param player: The APIPlayer to wrap
        :param executor: The ThreadPoolExecutor where the methods will be executed
        """
        self.player = player
        self.__executor = executor

    def name(self) -> str:
        """
        Returns the name of this player
        :return: A string representing this player's name
        """
        return self.player.name()

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> "Future[Any]":
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: a Future whose successful result would be an acknowledgment that the message has been received
        """
        return self.__executor.submit(self.player.setup, state, goal_position)

    def propose_board0(self, rows: int, columns: int) -> "Future[Board]":
        """
        A method for a player to propose a Board, the player will propose a random Board
        NOTE: We are working under the assumption that a board is still square and will thus create a square board
        of size NxN where N is equal to the maximum of rows and columns
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :return: a Future whose successful result would be a Board representing the Board this player proposes
        """
        return self.__executor.submit(self.player.propose_board0, rows, columns)

    def take_turn(self, current_state: RedactedState) -> "Future[Union[Move, Pass]]":
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: a Future whose successful result would be a Move or Pass representing the player's selection
        """
        return self.__executor.submit(self.player.take_turn, current_state)

    def win(self, did_win: bool) -> "Future[Any]":
        """
        Stores the given outcome of the game
        :param did_win: A boolean which is True if the player won (outright or tied), and False otherwise
        :return: a Future whose successful result would be an acknowledgment that the message has been received
        """
        return self.__executor.submit(self.player.win, did_win)

    def on_kicked(self) -> None:
        """
        A method to tear down any resources used in the construction of this SafeAPIPlayer. This does not trigger
        any interaction with the wrapped APIPlayer, no matter if it is local or remote.
        :return: None
        """

    def __repr__(self) -> str:
        """
        Overrides the repr method on a SafeAPIPlayer
        :return: a string representing this SafeAPIPlayer
        """
        return f"SafeAPIPlayer({self.player}, {self.__executor})"
