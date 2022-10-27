from .direction import Direction


def get_direction_string(direction: Direction):
    if direction == Direction.Down:
        return "DOWN"
    if direction == Direction.Up:
        return "UP"
    if direction == Direction.Right:
        return "RIGHT"
    if direction == Direction.Left:
        return "LEFT"
