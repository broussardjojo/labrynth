from gem import Gem
from shapes import Shape


class Tile:
    """
    A Tile is a game piece to make the board and has a Shape and two Gems.
    """
    def __init__(self, shape: Shape, gem1: Gem, gem2: Gem):
        """
        A constructor to create a tile, provided with a Shape and two Gems
        :param shape: A Shape which represents one of the four canonical shapes in the game labyrinth
        :param gem1: A Gem which represents one of the gems on the tile
        :param gem2: A Gem which represents the other gem on the tile
        """
        self.__shape = shape
        self.__gem1 = gem1
        self.__gem2 = gem2

    def get_gems(self) -> (Gem, Gem):
        return self.__gem1, self.__gem2

    def __eq__(self, other) -> bool:
        """
        Override of the equals method to allow us to create custom equality between two Tiles, a Tile is equal
         to another Tile when its shape is the same and both gems are the same
        :param other: The other Tile to compare to this tile for equality
        :return: True if the tiles are equal, False otherwise
        """
        if isinstance(other, Tile):
            return self.__shape == other.__shape \
                   and self.__gem1 == other.__gem1\
                   and self.__gem2 == other.__gem2
        return False
