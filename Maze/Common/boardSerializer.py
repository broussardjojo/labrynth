import functools
import sys
from json import JSONDecoder
from typing import List, Set
from shapes import Line, Cross, Corner, TShaped
from gem import Gem
from board import Board
from tile import Tile

# Dictionary to convert a shape character to a Shape
shape_dict = {
    '└': Corner(0),
    '┌': Corner(1),
    '┐': Corner(2),
    '┘': Corner(3),
    '│': Line(0),
    '─': Line(1),
    '┬': TShaped(0),
    '┤': TShaped(1),
    '┴': TShaped(2),
    '├': TShaped(3),
    '┼': Cross()
}


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


def get_gems(gem_name_list: List[str]) -> (Gem, Gem):
    """
    Retrieve a pair of gems given a list of Gem names
    :param gem_name_list: List of Gem names (hopefully two for our use case)
    :return: Two Gems objects
    """
    return Gem(gem_name_list[0]), Gem(gem_name_list[1])


def make_board(board_dict: dict) -> Board:
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
            shape = shape_dict[board_dict['connectors'][row][col]]
            gem1, gem2 = get_gems(board_dict['treasures'][row][col])
            tile_grid[row].append(Tile(shape, gem1, gem2))
    return Board.from_list_of_tiles(tile_grid)


def coord_custom_compare(coord_one: dict, coord_two: dict) -> int:
    """
    Custom comparator to compare two coordinates of this format: {"column#: col, "row#", row}
    :param coord_one: dictionary of this format: {"column#: col, "row#", row}
    :param coord_two: dictionary of this format: {"column#: col, "row#", row}
    :return: -1 if coord_one comes first in the grid, 1 if coord_two comes first in the grid, 0 if they are the same
    location (hopefully never for our use case)
    """
    if coord_one['row#'] < coord_two['row#']:
        return -1
    elif coord_one['row#'] > coord_two['row#']:
        return 1
    elif coord_one['column#'] < coord_two['column#']:
        return -1
    elif coord_one['column#'] > coord_two['column#']:
        return 1
    return 0


def get_json_obj_list() -> List[dict]:
    """
    Read standard input one JSON object at a time and convert it into a list of dictionaries
    :return: A list of dictionaries representing the two inputs (a board and a starting coordinate)
    """
    stdin = sys.stdin.read().lstrip()
    decoder = JSONDecoder()
    json_obj_list = []
    while len(stdin) > 0:
        json_obj, index = decoder.raw_decode(stdin)
        json_obj_list.append(json_obj)
        stdin = stdin[index:]
        stdin = stdin.lstrip()
    return json_obj_list


def get_output_list_from_reachable_tiles(reachable_list: Set[Tile], board: Board) -> List[dict]:
    """
    Formats a list of Tiles into a list of outputs in the specified format: {"column#: col, "row#", row}
    :param reachable_list: List of Tiles which represents the reachable Tiles
    :param board: A Board which represents the Board the reachable Tiles come from
    :return: A List of Dictionaries in the format: {"column#: col, "row#", row}
    """
    output_json_list = []
    for reachable_tile in reachable_list:
        row, col = get_index_by_tile_on_grid(reachable_tile, board.get_tile_grid())
        output_json_list.append(
            {'column#': col, 'row#': row}
        )
    return output_json_list


def main() -> List[dict]:
    """
    Main method which composes many helper methods to read input, make a board, get the reachable tiles, and sort them
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list()
    board = make_board(json_obj_list[0])
    coord_json = json_obj_list[1]
    base_tile = board.get_tile_grid()[coord_json['row#']][coord_json['column#']]
    reachable_list = board.reachable_tiles(base_tile)
    output_json_list = get_output_list_from_reachable_tiles(reachable_list, board)
    output_json_list.sort(key=functools.cmp_to_key(coord_custom_compare))
    return output_json_list


# Entry point main method
if __name__ == '__main__':
    print(main())
