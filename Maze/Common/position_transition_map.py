from typing import Dict, Any

from Maze.Common.position import Position


class PositionTransitionMap:
    """
    Represents the coordinate transitions performed by a single slide, see Board.slide_and_insert
    """
    updated_positions: Dict[Position, Position]
    removed_position: Position
    inserted_position: Position

    def __init__(self, updated_positions: Dict[Position, Position], removed_position: Position,
                 inserted_position: Position):
        """
        Creates a PositionTransitionMap given updated positions and removed positions
        :param updated_positions: a dictionary of updated positions representing a mapping of positions before a slide
         and after a slide
        :param removed_position: a position representing the old position of the tile moved off the board
        :param inserted_position: a position representing the new position of the tile inserted into the board
        """
        self.updated_positions = updated_positions
        self.removed_position = removed_position
        self.inserted_position = inserted_position

    def __eq__(self, other: Any) -> bool:
        """
        Overrides the __eq__ method of PositionTransitionMap objects
        :param other: The object being compared to this PositionTransitionMap
        :return: True if the updated, removed, and inserted positions match, otherwise false
        """
        if isinstance(other, PositionTransitionMap):
            return self.updated_positions == other.updated_positions and \
                   self.removed_position == other.updated_positions and \
                   self.inserted_position == other.inserted_position
        return False
