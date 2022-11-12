from typing import Any, Callable

from ..Common.direction import Direction
from ..Common.position import Position


class Pass:
    """
    A Class representing a Passed move, this means there is no sliding, inserting, rotating, or avatar moving
    """
    def __str__(self) -> str:
        """
        Override the to string method for a Pass
        :return: The string "Pass"
        """
        return "Pass"

    def __eq__(self, other: Any) -> bool:
        """
        Overrides equality so all Pass objects are equal
        :param other: An object to compare this Pass to
        :return: True if the given object is a Pass, False otherwise
        """
        return isinstance(other, Pass)

    @staticmethod
    def return_if_move_perform_action_if_pass(if_pass_perform_action: Callable[[], Any]) -> Any:
        """
        Method on a Pass which when called will return the result of calling the given function object
        NOTE: This method is intended to be used in tandem with the same method in a Move but could be used
        by itself without breaking anything
        :param if_pass_perform_action: A function object which takes in no parameters and returns anything
        NOTE: It is the caller's responsibility to ensure the return type of the function
        :return: Any depending on what the user requests this Pass to do
        """
        return if_pass_perform_action()

    def perform_move_or_pass(self, perform_move_action: "Callable[[Move], None]", perform_pass_action: "Callable[[Pass], None]") -> None:
        """
        Method on a Pass which will perform a given void action, when supplied with two void methods a Pass object
        calls the second one.
        NOTE: This method is intended to be used in tandem with the same method in a Move but could be used
        by itself without breaking anything
        :param perform_move_action: An unused argument describing the action to perform if this were a Move object
        :param perform_pass_action: A function object representing the action to perform from this pass
        :return: None
        """
        perform_pass_action(self)

    @staticmethod
    def format_output() -> str:
        """
        Method on a pass which will return a string representing a Pass
        NOTE: This method is intended to be used in tandem with the same method in a Move but could be used
        by itself without breaking anything
        :return: The string "PASS"
        """
        return "PASS"


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

    def return_if_move_perform_action_if_pass(self, if_pass_perform_action: Callable[[], Any]) -> None:
        """
        Acts as a getter for this Move object
        NOTE: This method is intended to be used in tandem with the same method in a Pass but could be used
        by itself without breaking anything
        :param if_pass_perform_action: an unused function object which is relevant for use in dynamic dispatch
        :return: This Move
        """
        return self

    def perform_move_or_pass(self, perform_move_action: "Callable[[Move], None]", perform_pass_action: "Callable[[Pass], None]") -> None:
        """
        Method on a Move which will perform a given void action, when supplied with two void methods a Move object
        calls the first one.
        NOTE: This method is intended to be used in tandem with the same method in a Pass but could be used
        by itself without breaking anything
        :param perform_move_action: A function object representing the action to perform from this Move
        :param perform_pass_action: An unused argument describing the action to perform if this were a Pass object
        :return: None
        """
        perform_move_action(self)

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
