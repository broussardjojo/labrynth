from typing import List

from .board import Board
from .utils import get_connector_from_shape


def get_connectors_helper(board: Board) -> List[List[str]]:
    list_of_connectors = []
    for row in range(board.get_height()):
        list_of_connectors.append([])
        for col in range(board.get_width()):
            list_of_connectors[row].append(get_connector_from_shape(board.get_tile_grid()[row][col].get_shape()))
    return list_of_connectors


def get_treasures_helper(board: Board) -> List[List[List[str]]]:
    list_of_gems = []
    for row in range(board.get_height()):
        list_of_gems.append([])
        for col in range(board.get_width()):
            gem1, gem2 = board.get_tile_grid()[row][col].get_gems()
            list_of_gems[row].append([str(gem1), str(gem2)])
    return list_of_gems


def get_serialized_board(board: Board) -> dict:
    board_dict = {
        "connectors": get_connectors_helper(board),
        "treasures": get_treasures_helper(board)
    }

    return board_dict
