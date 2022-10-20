from typing import List, Tuple
from .utils import get_json_obj_list
import sys
from .board import Board
from .boardSerializer import make_tile_grid
from .playerSerializer import make_list_of_players
from .state import State
from .direction import Direction


def make_previous_move(prev_move: Tuple[int, str]) -> Tuple[int, Direction]:
    return prev_move[0]

def main() -> List[dict]:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    tile_grid = make_tile_grid(json_obj_list[0]['board'])
    spare = make_spare_tile(json_obj_list[0]['spare'])
    board = Board(tile_grid, spare)
    players = make_list_of_players(json_obj_list[0]['players'])
    previous_move = make_previous_move(json_obj_list[0]['last'])
    state = State.from_current_state(board, players, previous_move)

    return output_json_list


# Entry point main method
if __name__ == '__main__':
    print(main())
