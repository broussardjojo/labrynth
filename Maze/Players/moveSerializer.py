from typing import List, Tuple, Optional

from ..Common.direction import Direction
from ..JSON.definitions import OptionalJSONAction
from ..JSON.serializers import direction_to_json


def get_serialized_last_action(moves: List[Tuple[int, Direction]]) -> OptionalJSONAction:
    """
    Returns the last move in a list of actions
    :param moves: the list of moves
    :return: a move if there was one in the given list, otherwise None
    """
    if not moves:
        return None
    slide_index, slide_direction = moves[-1]
    return [slide_index, direction_to_json(slide_direction)]
