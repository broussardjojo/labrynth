from enum import Enum
from typing import Tuple

from typing_extensions import assert_never

UP_OFFSET = -1
RIGHT_OFFSET = 1
DOWN_OFFSET = 1
LEFT_OFFSET = -1


class Direction(Enum):
    """
    An Enum representing one of the four directions a Tile can move: Up, Right, Down, or Left
    """
    Up = 1
    Right = 2
    Down = 3
    Left = 4

    def get_offset_tuple(self) -> Tuple[int, int]:
        """
        Gets the offset row col tuple for this Direction
        :return: a Tuple[int, int] representing the offset in this direction
        """
        if self is Direction.Up:
            return UP_OFFSET, 0
        if self is Direction.Right:
            return 0, RIGHT_OFFSET
        if self is Direction.Down:
            return DOWN_OFFSET, 0
        if self is Direction.Left:
            return 0, LEFT_OFFSET
        assert_never(self)

    def get_opposite_direction(self):
        """
        Get the opposite direction of this direction
        :return: A Direction representing the flipped Direction
        """
        if self is Direction.Up:
            return Direction.Down
        if self is Direction.Down:
            return Direction.Up
        if self is Direction.Right:
            return Direction.Left
        if self is Direction.Left:
            return Direction.Right
        assert_never(self)
