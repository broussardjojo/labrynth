from .strategy import Strategy
from ..Common.observableState import ObservableState
from ..Common.utils import ALL_NAMED_COLORS
from .move import Move
from .riemann import Riemann
from ..Common.position import Position
from ..Common.board import Board
from multipledispatch import dispatch
import re


class Player:
    """
    A Player is a representation of a player of a game of Labyrinth. A Player has a home position, a goal position and a
    current position, which defaults to their home position.
    """

    def __init__(self, home_position: Position, goal_position: Position,
                 current_position: Position, strategy: Strategy, color: str, name: str, age: int):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Positions to the respective fields
        :param home_position: the Position of this Player's home Tile where they begin the game
        :param goal_position: the Position of this Player's goal Tile
        :param strategy: the Strategy that this Player will employ to determine their next move
        :param color: the color that this Player will use; can be a hexcode RGB value or a color name
        """
        color_regex = re.compile("^([A-Fa-f0-9]{6})$")
        if color in ALL_NAMED_COLORS or re.search(
                color_regex, color):
            self.__color = color
        else:
            raise ValueError("Invalid Player Color")
        self.__home_position = home_position
        self.__goal_position = goal_position
        self.__current_position = current_position
        self.__strategy = strategy
        self.__name = name
        self.__age = age
        self.__has_won = False

    @classmethod
    def from_goal_home_color_strategy(cls, goal_position: Position, home_position: Position, color: str,
                                      strategy: Strategy):
        """
        Constructor to create a Player from a given goal position, home position, color, and strategy
        NOTE: Assigns current position to supplied home position (initializing a player). Assigns name to default name
        "helloworld" and age to default age 1.
        :param goal_position: a Position representing the goal Position of this Player
        :param home_position: a Position representing the home Position of this Player
        :param color: a string representing the color of this Player's avatar
        :param strategy: the Strategy that this Player will employ to determine their next move
        :return: an instance of a Player
        """
        current_position = home_position
        name = "helloworld"
        age = 1
        return cls(home_position, goal_position, current_position, strategy, color, name, age)

    @classmethod
    def from_current_home_color(cls, current_position: Position, home_position: Position, color: str):
        """
        Constructor to create a Player given a current position, home position, and color
        NOTE: makes four arbitrary decisions:
        1. Assigns the Player's goal to it's current Position
        2. Assigns the Player's strategy to Riemann
        Also Assigns name to default name "helloworld" and age to default age 1.
        :param current_position: a Position representing the current Position of this Player
        :param home_position: a Position representing the home Position of this Player
        :param color: a string representing the color of this Player's avatar
        :return: an instance of a Player
        """
        goal_position = current_position
        strategy = Riemann()
        name = "helloworld"
        age = 1
        return cls(home_position, goal_position, current_position, strategy, color, name, age)

    def get_home_position(self) -> Position:
        """
        Getter for __home_position
        :return: a Position representing the location of this Player's home on a Board
        """
        return self.__home_position

    def get_goal_position(self) -> Position:
        """
        Getter for __goal_position
        :return: a Position representing the location of this Player's goal on a Board
        """
        return self.__goal_position

    def get_current_position(self) -> Position:
        """
        Getter for __current_position
        :return: a Position representing the location of this Player's current tile on a Board
        """
        return self.__current_position

    def set_current_position(self, new_position: Position) -> None:
        """
        Setter for __current_position
        :return: None
        """
        self.__current_position = new_position

    def take_turn(self, current_state: ObservableState) -> Move:
        """
        Get the next move for this player based on it's Strategy
        :param current_state: an ObservableState representing the current state of the game
        :return: a Move representing this Player's next desired move
        """
        return self.__strategy.generate_move(current_state, self.__current_position, self.__goal_position)

    def get_color(self) -> str:
        """
        Getter for the current Player's color
        :return: The color of the current Player
        """
        return self.__color

    def name(self) -> str:
        """
        Getter for this Player's name
        :return: this Player's name
        """
        return self.__name

    # TODO: implement player acknowledgment to referee
    def won(self, has_won: bool) -> None:
        """
        Sets the has_won field for this Player to be the given boolean
        :param has_won: a boolean representing when this Player has won, True if they have, otherwise False
        :return: None
        """
        self.__has_won = has_won

    # TODO: implement player acknowledgment to referee
    # Note: while we are passing our user-defined types: ObservableState and Position, dispatch is only checking the
    # number of arguments, not their type, it treats all user-defined types as "object"
    @dispatch(ObservableState, Position)
    def setup(self, current_state: ObservableState, goal: Position) -> None:
        """
        Method to give this player the initial state of the board and its goal Position
        :param current_state: An ObservableState representing the initial State of the game
        :param goal: A Position representing the goal Position for this player
        :return: None
        """
        self.__goal_position = goal

    # Note: while we are passing our user-defined types: ObservableState and Position, dispatch is only checking the
    # number of arguments, not their type, it treats all user-defined types as "object"
    @dispatch(Position)
    def setup(self, home: Position) -> None:
        """
        An overloaded version of the setup method that doesn't take in the State of the game, this lack of parameter
        represents that this player has reached its goal and is being given a reminder to go home
        :param home: A Position representing the home Position of this player (which is its new goal to reach)
        :return: None
        """
        self.__goal_position = home

    @staticmethod
    def propose_board0(rows: int, columns: int, **kwargs) -> Board:
        """
        A method for a player to propose a Board, the player will propose a random Board which may be seeded
        NOTE: We are working under the assumption that a board is still square and will thus create a square board
        of size NxN where N is equal to the maximum of rows and columns
        :param rows: an int representing the minimum number of rows to make the Board from
        :param columns: an int representing the minimum number of columns to make the Board from
        :param kwargs: key word arguments that can be passed in, currently the only supported key word argument is
        seed
        :return: A Board representing the Board this player proposes
        """
        dimensions = max(rows, columns)
        if 'seed' in kwargs:
            return Board.from_random_board(dimensions, seed=kwargs['seed'])
        return Board.from_random_board(dimensions)

    def get_name(self) -> str:
        """
        Gets the name of this player
        :return: the name of this player as a string
        """
        return self.__name
