from enum import Enum
from typing import Tuple, List

from typing_extensions import assert_never

UP_OFFSET = -1
RIGHT_OFFSET = 1
DOWN_OFFSET = 1
LEFT_OFFSET = -1


class Direction(Enum):
    """
    An Enum representing one of the four directions a Tile can move: Up, Right, Down, or Left
    """
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    def get_offset_tuple(self) -> Tuple[int, int]:
        """
        Gets the offset row col tuple for this Direction
        :return: a Tuple[int, int] representing the offset in this direction
        """
        if self is Direction.UP:
            return UP_OFFSET, 0
        if self is Direction.RIGHT:
            return 0, RIGHT_OFFSET
        if self is Direction.DOWN:
            return DOWN_OFFSET, 0
        if self is Direction.LEFT:
            return 0, LEFT_OFFSET
        assert_never(self)

    def get_opposite_direction(self) -> "Direction":
        """
        Get the opposite direction of this direction
        :return: A Direction representing the flipped Direction
        """
        if self is Direction.UP:
            return Direction.DOWN
        if self is Direction.DOWN:
            return Direction.UP
        if self is Direction.RIGHT:
            return Direction.LEFT
        if self is Direction.LEFT:
            return Direction.RIGHT
        assert_never(self)

    @classmethod
    def horizontal_directions(cls) -> 'List[Direction]':
        return [Direction.LEFT, Direction.RIGHT]

    @classmethod
    def vertical_directions(cls) -> 'List[Direction]':
        return [Direction.UP, Direction.DOWN]
