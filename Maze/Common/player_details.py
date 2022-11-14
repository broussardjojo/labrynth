import re

from Maze.Common.utils import ALL_NAMED_COLORS
from Maze.Common.position import Position


class PlayerDetails:
    """
    A PlayerDetails is a representation of a player of a game of Labyrinth that has a home position, a
    current position, and a color.
    """

    _home_position: Position
    _current_position: Position
    _color: str

    def __init__(self, home_position: Position, current_position: Position, color: str):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Positions to the respective fields
        :param home_position: the Position of this Player's home Tile where they begin the game
        :param goal_position: the Position of this Player's goal Tile
        :param current_position: the current Position of this Player
        :param color: the color that this Player will use; can be a hexcode RGB value or a color name
        """
        color_regex = re.compile("^([A-Fa-f0-9]{6})$")
        if color in ALL_NAMED_COLORS or re.search(color_regex, color):
            self._color = color
        else:
            raise ValueError("Invalid Player Color")
        self._home_position = home_position
        self._current_position = current_position

    def get_home_position(self) -> Position:
        """
        Getter for __home_position
        :return: a Position representing the location of this Player's home on a Board
        """
        return self._home_position

    def get_current_position(self) -> Position:
        """
        Getter for __current_position
        :return: a Position representing the location of this Player's current tile on a Board
        """
        return self._current_position

    def set_current_position(self, new_position: Position) -> None:
        """
        Setter for __current_position
        :return: None
        """
        self._current_position = new_position

    def get_color(self) -> str:
        """
        Getter for the current Player's color
        :return: The color of the current Player
        """
        return self._color

    def __hash__(self) -> int:
        """
        Overrides the __hash__ method for Players. Uses the reference ID of the Player
        :return: An int representing the hash of the Player
        """
        return id(self)
