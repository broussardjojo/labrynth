import re

from ..Common.utils import ALL_NAMED_COLORS
from ..Common.position import Position


class Player:
    """
    A Player is a representation of a player of a game of Labyrinth. A Player has a home position, a goal position and a
    current position, which defaults to their home position.
    """

    __home_position: Position
    __goal_position: Position
    __current_position: Position
    __color: str

    def __init__(self, home_position: Position, goal_position: Position,
                 current_position: Position, color: str):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Positions to the respective fields
        :param home_position: the Position of this Player's home Tile where they begin the game
        :param goal_position: the Position of this Player's goal Tile
        :param current_position: the current Position of this Player
        :param color: the color that this Player will use; can be a hexcode RGB value or a color name
        """
        color_regex = re.compile("^([A-Fa-f0-9]{6})$")
        if color in ALL_NAMED_COLORS or re.search(color_regex, color):
            self.__color = color
        else:
            raise ValueError("Invalid Player Color")
        self.__home_position = home_position
        self.__goal_position = goal_position
        self.__current_position = current_position

    @classmethod
    def from_home_goal_color(cls, home_position: Position, goal_position: Position, color: str):
        """
        Constructor to create a Player from a given goal position, home position, and color
        :param home_position: a Position representing the home Position of this Player
        :param goal_position: a Position representing the goal Position of this Player
        :param color: a string representing the color of this Player's avatar
        :return: an instance of a Player
        """
        current_position = home_position
        return cls(home_position, goal_position, current_position, color)

    @classmethod
    def from_current_home_color(cls, current_position: Position, home_position: Position, color: str):
        """
        Constructor to create a Player given a current position, home position, and color
        TODO: makes an arbitrary decision to assigns the Player's goal to its current Position
        :param current_position: a Position representing the current Position of this Player
        :param home_position: a Position representing the home Position of this Player
        :param color: a string representing the color of this Player's avatar
        :return: an instance of a Player
        """
        goal_position = current_position
        return cls(home_position, goal_position, current_position, color)

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

    def set_goal_position(self, new_position: Position) -> None:
        """
        Setter for __goal_position
        :return: None
        """
        self.__goal_position = new_position

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

    def get_color(self) -> str:
        """
        Getter for the current Player's color
        :return: The color of the current Player
        """
        return self.__color

    def __hash__(self) -> int:
        """
        Overrides the __hash__ method for Players. Uses the reference ID of the Player
        :return: An int representing the hash of the Player
        """
        return id(self)