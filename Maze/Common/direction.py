from enum import Enum


class Direction(Enum):
    """
    An Enum representing one of the four directions a Tile can move: Up, Right, Down, or Left
    """
    Up = 1
    Right = 2
    Down = 3
    Left = 4
