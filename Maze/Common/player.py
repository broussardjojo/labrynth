from tile import Tile
from position import Position


class Player:
    def __init__(self, home_tile: Position, goal_tile: Position):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Tiles to the respective fields
        :param home_tile: this Player's home Tile where they begin the game
        :param goal_tile: this Player's goal Tile
        """
        self.__home_tile = home_tile
        self.__goal_tile = goal_tile
        self.__current_tile = home_tile

    def get_home_tile(self) -> Position:
        """
        Getter for __home_tile
        :return: a Tile representing this Player's home
        """
        return self.__home_tile

    def get_goal_tile(self) -> Position:
        """
        Getter for __goal_tile
        :return: a Tile representing this Player's goal
        """
        return self.__goal_tile

    def get_current_tile(self) -> Position:
        """
        Getter for __current_tile
        :return: a Tile representing this Player's current tile
        """
        return self.__current_tile

    def set_current_tile(self, new_tile: Position) -> None:
        """
        Setter for __current_tile
        :return: None
        """
        self.__current_tile = new_tile
