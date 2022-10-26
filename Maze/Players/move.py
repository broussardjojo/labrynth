from types import LambdaType, FunctionType
from typing import Any, Callable, Union

from ..Common.direction import Direction
from ..Common.position import Position


class Pass:
    def __str__(self):
        return "Pass"

    def __eq__(self, other):
        return isinstance(other, Pass)

    @staticmethod
    def return_move_recurse_pass(if_pass_perform_action: Callable[[], Any]):
        """
        Method on a Pass which when called will return the result of calling the given function object
        NOTE: This method is intended to be used in tandem with the same method in a Move but could be used
        by itself without breaking anything
        :param if_pass_perform_action: A function object which takes in no parameters and returns anything
        NOTE: It is the caller's responsibility to ensure the return type of the function
        :return: Any depending on what the user requests this Pass to do
        """
        return if_pass_perform_action()

    @staticmethod
    def perform_move_or_pass(perform_move_action: Callable[[], None], perform_pass_action: Callable[[], None]) -> None:
        perform_pass_action()


class Move:
    """
    A Class representing a Move which is valid move consisting of a slide index, slide Direction,
     spare tile rotation (in degrees), and a Position for the avatar to move to
    """
    def __init__(self, slide_index: int, slide_direction: Direction, spare_tile_rotation_degrees: int,
                 destination_position: Position):
        """
        A Constructor which assigns a slide index and Direction, tile rotation, destination Position
        :param slide_index: an int representing the row or column to slide
        :param slide_direction: a Direction representing the direction to slide the specified row
        :param spare_tile_rotation_degrees: an int representing the number of degrees to rotate the spare Tile
        :param destination_position: a Position to move the Player to
        """
        self.__slide_index = slide_index
        self.__slide_direction = slide_direction
        self.__spare_tile_rotation_degrees = spare_tile_rotation_degrees
        self.__destination_position = destination_position

    def get_slide_index(self) -> int:
        """
        Getter for the slide index
        :return: an int representing the index to slide
        """
        return self.__slide_index

    def get_slide_direction(self) -> Direction:
        """
        Getter for the slide direction
        :return: a Direction representing the direction to slide the specified row or column
        """
        return self.__slide_direction

    def get_spare_tile_rotation_degrees(self) -> int:
        """
        Getter for the spare tile rotation in degrees (can only be called when move is not a pass)
        :return: an int representing the spare tile rotation in degrees
        """
        return self.__spare_tile_rotation_degrees

    def get_destination_position(self) -> Position:
        """
        Getter for the destination Position (can only be called when move is not a pass)
        :return: a Position representing the position the Player should move to after sliding and inserting
        """
        return self.__destination_position

    def return_move_recurse_pass(self, if_pass_perform_action: Callable[[], Any]):
        """
        Acts as a getter for this Move object
        NOTE: This method is intended to be used in tandem with the same method in a Pass but could be used
        by itself without breaking anything
        :param if_pass_perform_action: an unused function object which is relevant for use in dynamic dispatch
        :return: This Move
        """
        return self

    @staticmethod
    def perform_move_or_pass(perform_move_action: Callable[[], None], perform_pass_action: Callable[[], None]) -> None:
        perform_move_action()

    def __eq__(self, other: Any) -> bool:
        """
        Override for equality to allow comparison of Moves
        :param other: Any (hopefully another Move) the other object to compare this Move to
        :return: True if the other object is a Move with the same slide index, direction, spare tile rotation, and
        destination position if the move is not a pass, False otherwise
        """
        if isinstance(other, Move):
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
               f"{self.__spare_tile_rotation_degrees}, Destination: {self.__destination_position}"