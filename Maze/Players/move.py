from typing import Any

from ..Common.direction import Direction
from ..Common.position import Position


class Move:
    """
    A Class representing a Move which is either:
     A valid move consisting of a slide index, slide Direction, spare tile rotation (in degrees), and a Position for
     the avatar to move to
     A pass move which does not allow access to the sliding, rotating, and moving information (which may be
      garbage values)
    """
    def __init__(self, slide_index: int, slide_direction: Direction, spare_tile_rotation_degrees: int,
                 destination_position: Position, pass_move: bool):
        """
        A Constructor which assigns a slide index and Direction, tile rotation, destination Position, and a boolean
        representing whether this Move is a pass or not
        :param slide_index: an int representing the row or column to slide
        :param slide_direction: a Direction representing the direction to slide the specified row
        :param spare_tile_rotation_degrees: an int representing the number of degrees to rotate the spare Tile
        :param destination_position: a Position to move the Player to
        :param pass_move: a bool which is True if this move is a pass, False otherwise
        """
        self.__slide_index = slide_index
        self.__slide_direction = slide_direction
        self.__spare_tile_rotation_degrees = spare_tile_rotation_degrees
        self.__destination_position = destination_position
        self.__pass_move = pass_move

    def is_pass(self) -> bool:
        """
        Determine if this method is a pass or valid move
        :return: True if this move is a pass, False otherwise
        """
        return self.__pass_move

    def get_slide_index(self) -> int:
        """
        Getter for the slide index (can only be called when move is not a pass)
        :return: an int representing the index to slide
        :raises: ValueError if the getter is called on a pass move
        """
        if self.is_pass():
            raise ValueError("Cannot access slide index of a pass move")
        return self.__slide_index

    def get_slide_direction(self) -> Direction:
        """
        Getter for the slide direction (can only be called when move is not a pass)
        :return: a Direction representing the direction to slide the specified row or column
        :raises: ValueError if the getter is called on a pass move
        """
        if self.is_pass():
            raise ValueError("Cannot access slide direction of a pass move")
        return self.__slide_direction

    def get_spare_tile_rotation_degrees(self) -> int:
        """
        Getter for the spare tile rotation in degrees (can only be called when move is not a pass)
        :return: an int representing the spare tile rotation in degrees
        :raises: ValueError if the getter is called on a pass move
        """
        if self.is_pass():
            raise ValueError("Cannot access degree of a pass move")
        return self.__spare_tile_rotation_degrees

    def get_destination_position(self) -> Position:
        """
        Getter for the destination Position (can only be called when move is not a pass)
        :return: a Position representing the position the Player should move to after sliding and inserting
        :raises: ValueError if the getter is called on a pass move
        """
        if self.is_pass():
            raise ValueError("Cannot access destination of a pass move")
        return self.__destination_position

    def __eq__(self, other: Any) -> bool:
        """
        Override for equality to allow comparison of Moves
        :param other: Any (hopefully another Move) the other object to compare this Move to
        :return: True if the other object is a Move with the same slide index, direction, spare tile rotation, and
        destination position if the move is not a pass. True if both moves are passes (all passes are equal regardless
        of other information). False otherwise
        """
        if isinstance(other, Move):
            if not other.__pass_move and not self.__pass_move:
                return True
            return other.__slide_index == self.__slide_index and other.__slide_direction == self.__slide_direction \
                   and other.__spare_tile_rotation_degrees == self.__spare_tile_rotation_degrees \
                   and other.__destination_position == self.__destination_position
        return False

    def __str__(self) -> str:
        """
        Override for string casting method to help with debugging and visualizing Move objects
        :return: A string representing important information about this Move
        """
        return f"Index: {self.__slide_index}, Direction: {self.__slide_direction}, Spare Rotation: " \
               f"{self.__spare_tile_rotation_degrees}, Destination: {self.__destination_position}, " \
               f"Pass: {self.__pass_move}"
