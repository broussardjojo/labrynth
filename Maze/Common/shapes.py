from abc import ABC
from .direction import Direction


class Shape(ABC):
    """
    A Shape is one of: Corner, Line, TShaped, or Cross and has four booleans representing paths that can be walked on
    """
    def __init__(self, top: bool, right: bool, bottom: bool, left: bool):
        self.__left = left
        self.__right = right
        self.__top = top
        self.__bottom = bottom

    def rotate(self, rotations: int) -> None:
        """
        This method rotates this Shape n times, where n is the number of rotations passed in.
        side effect: mutates the Shape's paths
        :param rotations: int which represents the number of 90 degree rotations to perform on the Shape, must be a
        positive number
        :return: None
        """
        for i in range(rotations):
            self.__rotate_helper()

    def __rotate_helper(self) -> None:
        """
        This method rotates this Shape 90 degrees to the right
        side effect: mutates the Shape's paths
        :return: None
        """
        old_top: bool = self.__top
        old_bottom: bool = self.__bottom
        old_left: bool = self.__left
        old_right: bool = self.__right

        self.__top = old_left
        self.__right = old_top
        self.__bottom = old_right
        self.__left = old_bottom

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
        return hash(self.__right) * hash(self.__left) + hash(self.__top) ^ hash(self.__bottom)


class Corner(Shape):
    """
    A Corner is a Shape and represents one of the four corner characters, its default orientation is └
    """
    def __init__(self, rotations: int):
        """
        Initializes the default Corner orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :raises ValueError if the base rotations are less than 0
        """
        super().__init__(True, True, False, False)
        if rotations < 0:
            raise ValueError("Invalid Corner Shape")
        self.rotate(rotations)


class Line(Shape):
    """
    A Line is a Shape and represents one of the two line characters, its default orientation is │
    """
    def __init__(self, rotations: int):
        """
        Initializes the default Line orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :raises ValueError if the base rotations are less than 0
        """
        super().__init__(True, False, True, False)
        if rotations < 0:
            raise ValueError("Invalid Line Shape")
        self.rotate(rotations)


class TShaped(Shape):
    """
    A TShaped is a Shape and represents one of the four T-Shaped characters, its default orientation is ┬
    """
    def __init__(self, rotations: int):
        """
        Initializes the default T-Shaped orientation and rotates to the desired shape
        :param rotations: The number of 90 degree rotations to perform upon initialization, must be positive
        :raises ValueError if the base rotations are less than 0
        """
        super().__init__(False, True, True, True)
        if rotations < 0:
            raise ValueError("Invalid T-Shape")
        self.rotate(rotations)


class Cross(Shape):
    """
    A Cross is a Shape and represents one of the one cross character, its default and only orientation is ┼
    """
    def __init__(self):
        """
        Initializes the cross shaped orientation
        """
        super().__init__(True, True, True, True)
