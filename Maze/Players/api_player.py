import atexit
import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Union, cast

from typing_extensions import Literal

from Maze.Common.signal_listener import SignalListener
from Maze.Players.move import Pass, Move
from Maze.Players.strategy import Strategy
from Maze.Common.board import Board
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Common.utils import Just, Maybe, Nothing

Acknowledgement = Any
ACK_OBJECT = object()

BadMethodName = Union[Literal["setup"], Literal["take_turn"], Literal["win"]]


class APIPlayer(ABC):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html.
    """

    @abstractmethod
    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: an acknowledgment that the message has been received
        """

    @abstractmethod
    def propose_board0(self, rows: int, columns: int) -> Board:
        """
        A method for a player to propose a Board
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :return: A Board representing the Board this player proposes
        """

    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of this player
        :return: A string representing this player's name
        """

    @abstractmethod
    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: A Move or Pass representing the player's selection action on its turn
        """

    @abstractmethod
    def win(self, did_win: bool) -> Acknowledgement:
        """
        Informs this player of the given outcome of the game
        :param did_win: A boolean which is True if the player won (outright or tied), and False otherwise
        :return: an acknowledgment that the message has been received
        """


class LocalPlayer(APIPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html. It runs locally.
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

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        """
        Informs this player of its goal position, and optionally the initial state of the game
        :param state: The initial state of the game, or None if this is not the first setup call
        :param goal_position: The player's goal position
        :return: an acknowledgment that the message has been received
        """
        self.__goal_position = Just(goal_position)
        return ACK_OBJECT

    def propose_board0(self, rows: int, columns: int) -> Board:
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

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        """
        Gets the next move for this player based on its Strategy
        :param current_state: a State representing the current state of the game
        :return: A Move or Pass representing the player's selection action on its turn
        """
        goal_pos = self.__goal_position.get("take_turn must not be called before setup")
        current_position = current_state.get_active_player_position()
        return self.__strategy.generate_move(current_state, goal_pos)

    def win(self, did_win: bool) -> Acknowledgement:
        """
        Stores the given outcome of the game
        :param did_win: A boolean which is True if the player won (outright or tied), and False otherwise
        :return: an acknowledgment that the message has been received
        """
        self.__won = Just(did_win)
        return ACK_OBJECT

    def __repr__(self) -> str:
        """
        Overrides the repr method on an APIPlayer
        :return: a string representing this APIPlayer
        """
        return f"APIPlayer({self.__name}, {self.__strategy})"


class BadLocalPlayer(LocalPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html. It runs locally, and runs correctly until one
    'bad method' is called, at which point it raises an exception by attempting '1 // 0'
    """

    def __init__(self, name: str, strategy: Strategy, bad_method_name: BadMethodName):
        super().__init__(name, strategy)
        self.__bad_method_name = bad_method_name

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        if self.__bad_method_name == "setup":
            return 1 // 0
        return super().setup(state, goal_position)

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        if self.__bad_method_name == "take_turn":
            return cast(Pass, 1 // 0)
        return super().take_turn(current_state)

    def win(self, did_win: bool) -> Acknowledgement:
        if self.__bad_method_name == "win":
            return 1 // 0
        return super().win(did_win)


class EventuallyBadLocalPlayer(LocalPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html. It runs locally, and runs correctly until one
    'bad method' is called, at which point it raises an exception by attempting '1 // 0'
    """
    __method_calls: int
    __bad_method_name: str
    __num_valid_calls: int

    def __init__(self, name: str, strategy: Strategy, bad_method_name: BadMethodName, num_valid_calls: int):
        super().__init__(name, strategy)
        if not 1 <= num_valid_calls <= 7:
            raise ValueError("Invalid number of valid calls, must be in range [1, 7]")
        self.__bad_method_name = bad_method_name
        self.__method_calls = 0
        self.__num_valid_calls = num_valid_calls

    @staticmethod
    def __sleep_forever() -> None:
        is_alive = True

        def die() -> None:
            nonlocal is_alive
            is_alive = False

        atexit.register(die)
        SignalListener.instance.add_handler(die)
        while is_alive:
            time.sleep(0.01)

    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        if self.__bad_method_name == "setup":
            self.__method_calls += 1
            if self.__method_calls >= self.__num_valid_calls:
                self.__sleep_forever()
        return super().setup(state, goal_position)

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        if self.__bad_method_name == "take_turn":
            self.__method_calls += 1
            if self.__method_calls >= self.__num_valid_calls:
                self.__sleep_forever()
        return super().take_turn(current_state)

    def win(self, did_win: bool) -> Acknowledgement:
        if self.__bad_method_name == "win":
            self.__method_calls += 1
            if self.__method_calls >= self.__num_valid_calls:
                self.__sleep_forever()
        return super().win(did_win)
