from abc import ABC, abstractmethod
from typing import Tuple, Optional

from .direction import Direction


ShapeTuple = Tuple[bool, bool, bool, bool]


class Shape(ABC):
    """
    A Shape is one of: Corner, Line, TShaped, or Cross and has four booleans representing paths that can be walked on
    """
    def __init__(self, top: bool, right: bool, bottom: bool, left: bool):
        self.__left = left
        self.__right = right
        self.__top = top
        self.__bottom = bottom

    @staticmethod
    def _rotate_helper(old_connections: ShapeTuple, rotations: int) -> ShapeTuple:
        """
        Computes the rotated form of the given (top, right, bottom, left) shape tuple.
        :param old_connections: A ShapeTuple representing the connections of the shape
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape
        :return: A ShapeTuple representing the connections of the shape after rotation
        """
        old_top, old_right, old_bottom, old_left = old_connections
        num_rotations = rotations % 4
        if num_rotations == 0:
            return old_top, old_right, old_bottom, old_left
        elif num_rotations == 1:
            return old_left, old_top, old_right, old_bottom
        elif num_rotations == 2:
            return old_bottom, old_left, old_top, old_right
        else:
            return old_right, old_bottom, old_left, old_top

    def get_orientation_tuple(self) -> ShapeTuple:
        """
        Returns the (top, right, bottom, left) shape tuple corresponding to this shape.
        :return: A ShapeTuple representing the connections of this shape
        """
        return self.__top, self.__right, self.__bottom, self.__left

    @abstractmethod
    def rotate(self, rotations: int) -> "Shape":
        """
        This method rotates this Shape n times, where n is the number of rotations passed in.
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape, must be a
        positive number
        :return: The rotated shape
        """
        pass

    def __eq__(self, other) -> bool:
        """
        Overrides equals. This Shape is equal to another Shape if they have the same paths.
        :param other: Any, to be compared to this Shape
        :return: True if the Shape and other are equal, otherwise false
        """
        if isinstance(other, Shape):
            return self.__top == other.__top \
                   and self.__left == other.__left \
                   and self.__right == other.__right \
                   and self.__bottom == other.__bottom
        return False

    def has_path(self, path_direction: Direction) -> bool:
        """
        Determines whether this Shape has a path in the given Direction
        :param path_direction: a Direction representing the path to check
        :return: True if this Shape has a path in the given Direction, otherwise False
        """
        if path_direction == Direction.Right:
            return self.__right
        elif path_direction == Direction.Left:
            return self.__left
        elif path_direction == Direction.Up:
            return self.__top
        else:
            return self.__bottom

    def __hash__(self):
        """
        Overrides a hash for a Shape (using different math operations to prevent collisions with shapes that are rotated
        versions of themselves)
        :return: An int representing the hash of a Shape
        """
        return hash((self.__top, self.__right, self.__bottom, self.__left))

    def __str__(self):
        """
        Override the to string method for a shape
        :return: A string representing the paths of this shapes
        """
        return f"Top: {self.__top} Right: {self.__right} Bottom: {self.__bottom} Left: {self.__left}"


class Corner(Shape):
    """
    A Corner is a Shape and represents one of the four corner characters, its default orientation is └
    """

    rotation: int

    def __init__(self, rotations: int, relative_to: Optional["Corner"] = None):
        """
        Initializes the default Corner orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :param relative_to: An optional Corner to base the rotation from. If not provided, the base orientation is "└"
        :raises ValueError if the base rotations are less than 0
        """
        if rotations < 0:
            raise ValueError("Invalid Corner Shape")
        if relative_to is None:
            base_orientation = (True, True, False, False)
        else:
            base_orientation = relative_to.get_orientation_tuple()
        top, right, bottom, left = Shape._rotate_helper(base_orientation, rotations)
        super().__init__(top, right, bottom, left)

    def rotate(self, rotations: int) -> "Corner":
        """
        This method rotates this Shape n times, where n is the number of rotations passed in.
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape, must be a
        positive number
        :raises ValueError if the number of rotations is less than 0
        :return: The rotated shape
        """
        return Corner(rotations, relative_to=self)

class Line(Shape):
    """
    A Line is a Shape and represents one of the two line characters, its default orientation is │
    """

    def __init__(self, rotations: int, relative_to: Optional["Line"] = None):
        """
        Initializes the default Line orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :param relative_to: An optional Line to base the rotation from. If not provided, the base orientation is "│"
        :raises ValueError if the base rotations are less than 0
        """
        if rotations < 0:
            raise ValueError("Invalid Line Shape")
        if relative_to is None:
            base_orientation = (True, False, True, False)
        else:
            base_orientation = relative_to.get_orientation_tuple()
        top, right, bottom, left = Shape._rotate_helper(base_orientation, rotations)
        super().__init__(top, right, bottom, left)

    def rotate(self, rotations: int) -> "Line":
        """
        This method rotates this Shape n times, where n is the number of rotations passed in.
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape, must be a
        positive number
        :raises ValueError if the number of rotations is less than 0
        :return: The rotated shape
        """
        return Line(rotations, relative_to=self)


class TShaped(Shape):
    """
    A TShaped is a Shape and represents one of the four T-Shaped characters, its default orientation is ┬
    """

    def __init__(self, rotations: int, relative_to: Optional["TShaped"] = None):
        """
        Initializes the default TShaped orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :param relative_to: An optional TShaped to base the rotation from. If not provided, the base orientation is "┬"
        :raises ValueError if the base rotations are less than 0
        """
        if rotations < 0:
            raise ValueError("Invalid T-Shape")
        if relative_to is None:
            base_orientation = (False, True, True, True)
        else:
            base_orientation = relative_to.get_orientation_tuple()
        top, right, bottom, left = Shape._rotate_helper(base_orientation, rotations)
        super().__init__(top, right, bottom, left)

    def rotate(self, rotations: int) -> "TShaped":
        """
        This method rotates this Shape n times, where n is the number of rotations passed in.
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape, must be a
        positive number
        :raises ValueError if the number of rotations is less than 0
        :return: The rotated shape
        """
        return TShaped(rotations, relative_to=self)


class Cross(Shape):
    """
    A Cross is a Shape and represents one of the one cross character, its default and only orientation is ┼
    """
    def __init__(self):
        """
        Initializes the cross shaped orientation
        """
        super().__init__(True, True, True, True)

    def rotate(self, rotations: int) -> "Cross":
        return self
