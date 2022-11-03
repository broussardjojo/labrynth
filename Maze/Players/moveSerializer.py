from typing import List, Tuple, Optional
from ..Common.directionSerializer import get_direction_string
from ..Players.move import Move


def get_serialized_last_action(moves: List[Move]) -> Optional[Tuple[int, str]]:
    if not moves:
        return None
    slide_index, slide_direction = moves[-1]
    return slide_index, get_direction_string(slide_direction)
