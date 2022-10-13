import json
import sys
from json import JSONDecoder
from typing import List

from shapes import Line, Cross, Corner, TShaped
from gem import Gem
from board import Board
from tile import Tile

shape_dict = {
    '└': Corner(0),
    '┌': Corner(1),
    '┐': Corner(2),
    '┘': Corner(3),
    '│': Line(0),
    '─': Line(1),
    '┬': TShaped(0),
    '├': TShaped(1),
    '┴': TShaped(2),
    '┤': TShaped(3),
    '┼': Cross
}


def get_index_by_tile_on_grid(base_tile: Tile, tile_grid: List[List[Tile]]) -> (int, int):
    for row in range(len(tile_grid)):
        for col in range(len(tile_grid[row])):
            if tile_grid[row][col] == base_tile:
                return row, col


def get_gems(gem_name_list: List[str]):
    return Gem(gem_name_list[0]), Gem(gem_name_list[1])


def make_board(board_dict: dict) -> Board:
    tile_grid = []
    for row in range(len(board_dict['connectors'])):
        tile_grid.append([])
        for col in range(len(board_dict['connectors'][row])):
            shape = shape_dict[board_dict['connectors'][row][col]]
            gem1, gem2 = get_gems(board_dict['treasures'][row][col])
            tile_grid[row].append(Tile(shape, gem1, gem2))
    return Board.from_list_of_tiles(tile_grid)


def main():
    stdin = sys.stdin.read().lstrip()
    decoder = JSONDecoder()
    json_obj_list = []
    while len(stdin) > 0:
        json_obj, index = decoder.raw_decode(stdin)
        json_obj_list.append(json_obj)
        # remove previously read object from string
        stdin = stdin[index:]
        stdin = stdin.lstrip()
    board = make_board(json_obj_list[0])
    coord_json = json_obj_list[1]
    base_tile = board.get_tile_grid()[coord_json['column#']][coord_json['row#']]
    reachable_list = board.reachable_tiles(base_tile)
    output_json_list = []
    for reachable_tile in reachable_list:
        row, col = get_index_by_tile_on_grid(reachable_tile, board.get_tile_grid())
        output_json_list.append(
            {'column#': col, 'row#': row}
        )
    return output_json_list


if __name__ == '__main__':
    print(main())
