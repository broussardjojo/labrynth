import functools
import json
from typing import Tuple
from .utils import get_json_obj_list, coord_custom_compare
import sys
from .board import Board
from .boardSerializer import make_tile_grid, make_individual_tile, get_output_list_from_reachable_tiles
from .playerSerializer import make_list_of_players
from .state import State
from .direction import Direction


def get_direction_from_direction_str(direction_str: str) -> Direction:
    if direction_str == "DOWN":
        return Direction.Down
    if direction_str == "UP":
        return Direction.Up
    if direction_str == "RIGHT":
        return Direction.Right
    return Direction.Left


def make_previous_move(prev_move: Tuple[int, str]) -> Tuple[int, Direction]:
    return prev_move[0], get_direction_from_direction_str(prev_move[1])


def main() -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    tile_grid = make_tile_grid(json_obj_list[0]['board'])
    spare = make_individual_tile(json_obj_list[0]['spare'])
    board = Board(tile_grid, spare)
    players = make_list_of_players(json_obj_list[0]['plmt'])
    previous_move = make_previous_move(json_obj_list[0]['last'])
    state = State.from_current_state(board, players, previous_move)
    board = state.get_board()
    slide_index = json_obj_list[1]
    slide_direction = get_direction_from_direction_str(json_obj_list[2])
    rotate_degrees = json_obj_list[3]
    state.rotate_spare_tile(rotate_degrees)
    state.slide_and_insert(slide_index, slide_direction)
    current_player = state.get_players()[0]
    current_player_position = current_player.get_current_position()
    current_player_tile = board.get_tile_by_position(current_player_position)
    reachable_tiles = board.reachable_tiles(current_player_tile)
    output_list = get_output_list_from_reachable_tiles(reachable_tiles, state.get_board())
    output_list.sort(key=functools.cmp_to_key(coord_custom_compare))
    json_output_list = json.dumps(output_list)
    json_output_list_no_spaces = json_output_list.replace(' ', '')
    return json_output_list_no_spaces


# Entry point main method
if __name__ == '__main__':
    print(main())
