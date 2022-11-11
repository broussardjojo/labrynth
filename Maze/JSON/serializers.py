from typing_extensions import assert_never

from .definitions import JSONDirection, JSONChoiceMove, JSONCoordinate
from ..Common.direction import Direction
from ..Common.position import Position
from ..Players.move import Move


def direction_to_json(direction: Direction) -> JSONDirection:
    """
    Gets the string representation of the given direction
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


def position_to_json(position: Position) -> JSONCoordinate:
    """
    Gets the JSON representation of the given position
    :param position: A Position
    :return: A JSONCoordinate dictionary in the format {"row#": int, "column#": int}
    """
    return {"row#": position.get_row(), "column#": position.get_col()}


def move_to_json(self: Move) -> JSONChoiceMove:
    """
    Gets the JSON representation of the given move
    :return: a List containing this Move's slide index, slide direction, spare tile rotation degrees,
     and avatar move JSONCoordinate
    """
    index = self.get_slide_index()
    direction = self.get_slide_direction()
    degrees_clockwise = self.get_spare_tile_rotation_degrees()
    destination_pos = self.get_destination_position()
    # Note that we convert to counterclockwise
    return [index,
            direction_to_json(direction),
            -degrees_clockwise % 360,
            position_to_json(destination_pos)]


