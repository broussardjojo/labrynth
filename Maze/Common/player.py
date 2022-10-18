from tile import Tile
from position import Position


class Player:
    def __init__(self, home_position: Position, goal_position: Position):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Positions to the respective fields
        :param home_position: the Position of this Player's home Tile where they begin the game
        :param goal_position: the Position of this Player's goal Tile
        """
        self.__home_position = home_position
        self.__goal_position = goal_position
        self.__current_position = home_position

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
