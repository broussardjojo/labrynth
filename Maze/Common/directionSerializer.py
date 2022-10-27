from .direction import Direction


def get_direction_string(direction: Direction) -> str:
    """
    Gets the string of the given direction
    :param direction: the Direction representing the direction to translate
    :return: a string representing a direction
    """
    if direction == Direction.Down:
        return "DOWN"
    if direction == Direction.Up:
        return "UP"
    if direction == Direction.Right:
        return "RIGHT"
    if direction == Direction.Left:
        return "LEFT"
