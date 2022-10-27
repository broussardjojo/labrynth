import functools
import sys
from typing import List, Set
from copy import deepcopy
from .gem import Gem
from .board import Board
from .tile import Tile
from .utils import get_json_obj_list, shape_dict, coord_custom_compare
from .positionSerializer import get_position_dict


def get_output_list_from_reachable_tiles(reachable_list: Set[Tile], board: Board) -> List[dict]:
    """
    Formats a list of Tiles into a list of outputs in the specified format: {"column#: col, "row#", row}
    :param reachable_list: List of Tiles which represents the reachable Tiles
    :param board: A Board which represents the Board the reachable Tiles come from
    :return: A List of Dictionaries in the format: {"column#: col, "row#", row}
    """
    output_json_list = []
    for reachable_tile in reachable_list:
        reachable_tile_position = board.get_position_by_tile(reachable_tile)
        output_json_list.append(get_position_dict(reachable_tile_position))
    return output_json_list


def get_index_by_tile_on_grid(base_tile: Tile, tile_grid: List[List[Tile]]) -> (int, int):
    """
    Get the index coordinates of a Tile in a provided List[List[Tiles]]
    :param base_tile: The Tile to look for in the grid
    :param tile_grid: The 2D list of Tiles to search in
    :return: A coordinate pair representing the location of a Tile on the given grid
    """
    for row in range(len(tile_grid)):
        for col in range(len(tile_grid[row])):
            if tile_grid[row][col] == base_tile:
                return row, col


def make_tile_grid(board_dict: dict) -> List[List[Tile]]:
    """
    Makes a board given a dictionary of connectors and treasures
    :param board_dict: A dictionary of connectors and treasures in the following format
    {"connectors": List[List[Shape Characters]], "treasures": List[List[List[Gem Name Strings]]]
    :return: A Board object filled with all the tiles designated by the provided dictionary
    """
    tile_grid = []
    for row in range(len(board_dict['connectors'])):
        tile_grid.append([])
        for col in range(len(board_dict['connectors'][row])):
            shape = deepcopy(shape_dict[board_dict['connectors'][row][col]])
            gem1, gem2 = get_gems(board_dict['treasures'][row][col])
            tile = Tile(shape, gem1, gem2)
            tile_grid[row].append(tile)
    return tile_grid


def make_individual_tile(tile_dict: dict) -> Tile:
    shape = shape_dict[tile_dict['tilekey']]
    gem1, gem2 = get_gems([tile_dict["1-image"], tile_dict["2-image"]])
    return Tile(shape, gem1, gem2)


def get_gems(gem_name_list: List[str]) -> (Gem, Gem):
    """
    Retrieve a pair of gems given a list of Gem names
    :param gem_name_list: List of Gem names (hopefully two for our use case)
    :return: Two Gems objects
    """
    return Gem(gem_name_list[0]), Gem(gem_name_list[1])


def main() -> List[dict]:
    """
    Main method which composes many helper methods to read input, make a board, get the reachable tiles, and sort them
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    board = Board.from_list_of_tiles(make_tile_grid(json_obj_list[0]))
    coord_json = json_obj_list[1]
    base_tile = board.get_tile_grid()[coord_json['row#']][coord_json['column#']]
    reachable_list = board.reachable_tiles(base_tile)
    output_json_list = get_output_list_from_reachable_tiles(reachable_list, board)
    output_json_list.sort(key=functools.cmp_to_key(coord_custom_compare))
    return output_json_list


# Entry point main method
if __name__ == '__main__':
    print(main())
