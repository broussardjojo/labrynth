from typing import Tuple

from .direction import Direction
from .gem import Gem
from .shapes import Shape


class Tile:
    """
    A Tile is a game piece to make the board and has a Shape and two Gems.
    """

    FULL_ROTATION = 4

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

    def get_gems(self) -> Tuple[Gem, Gem]:
        """
        Returns a list containing both gems found on this tile.
        :return: a list of gems found on this tile
        """
        return self.__gem1, self.__gem2

    def get_shape(self) -> Shape:
        """
        Returns the Shape found on this tile.
        :return: the Shape found on this tile
        """
        return self.__shape

    def same_gems_on_tiles(self, gem1: Gem, gem2: Gem) -> bool:
        """
        Checks this Tile has the same gems as the given Gems.
        :param gem1: the first Gem being compared to this Tile's gems
        :param gem2: the second Gem being compared to this Tile's gems
        :return: True if this Tile contains the given two gems, false otherwise
        """
        return (gem1 == self.__gem1 and gem2 == self.__gem2) or \
               (gem1 == self.__gem2 and gem2 == self.__gem1)

    def __eq__(self, other) -> bool:
        """
        Override of the equals method to allow us to create custom equality between two Tiles, a Tile is equal
         to another Tile when its shape is the same and both gems are the same
        :param other: The other Tile to compare to this tile for equality
        :return: True if the tiles are equal, False otherwise
        """
        if isinstance(other, Tile):
            return self.__shape == other.__shape \
                   and ((self.__gem1 == other.__gem1 and self.__gem2 == other.__gem2)
                        or (self.__gem1 == other.__gem2 and self.__gem2 == other.__gem1))
        return False

    def __hash__(self) -> int:
        """
        Overrides the hash method for a Tile (allowing it to be used a key)
        :return: An int representing the hash of this Tile
        """
        return hash(self.__shape) + hash(self.__gem2) + hash(self.__gem1)

    def has_path(self, path_direction: Direction) -> bool:
        """
        Determines if this Tile has a path in the given direction
        :param path_direction: a Direction representing the direction to check for a path
        :return: True if this Tile has a path in the given direction, otherwise False
        """
        return self.__shape.has_path(path_direction)

    def rotate(self, rotations: int) -> None:
        """
        Rotates this Tile the given number of times.
        :param rotations: an int representing how many times to rotate this Tile (clockwise)
        :return: None
        side effect: mutates the Shape of this Tile
        """
        positive_rotations = self.__get_positive_rotations(rotations)
        self.__shape = self.__shape.rotate(positive_rotations)

    def __get_positive_rotations(self, rotations: int) -> int:
        """
        Gives the positive equivalent of Tile rotations from the given number of rotations.
        :param rotations: an int representing how many times to rotate this Tile
        :return: an int representing how many times to rotate this Tile
        """
        return (rotations % self.FULL_ROTATION) + self.FULL_ROTATION

    def __str__(self) -> str:
        """
        Overrides the __str__ method of Tiles
        :return: A string describing this tile's shape and gems
        """
        return f"Shape: {str(self.__shape)} Gem1: {str(self.__gem1)} Gem2: {str(self.__gem2)}"
