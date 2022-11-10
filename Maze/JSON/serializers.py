from typing_extensions import assert_never

from .definitions import JSONDirection
from ..Common.direction import Direction


def direction_to_json(direction: Direction) -> JSONDirection:
    """
    Gets the string of the given direction
    :param direction: the Direction representing the direction to translate
    :return: a string representing a direction
    """
    if direction is Direction.Down:
        return "DOWN"
    elif direction is Direction.Up:
        return "UP"
    elif direction is Direction.Right:
        return "RIGHT"
    elif direction is Direction.Left:
        return "LEFT"
    else:
        assert_never(direction)

