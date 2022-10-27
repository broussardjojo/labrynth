import json
from ..Common.utils import get_json_obj_list
from ..Common.boardSerializer import make_tile_grid, make_individual_tile
from ..Players.playerSerializer import make_player_with_all_information
from ..Common.observableState import ObservableState
from ..Common.position import Position
from ..Common.board import Board
from .riemann import Riemann
from .euclid import Euclid
from .strategy import Strategy
import sys


def make_strategy(strategy_name: str) -> Strategy:
    """
    Create either a Riemann or Euclid strategy
    :param strategy_name: either Riemann or Euclid
    :return: Either a Riemann or Euclid Strategy
    """
    if strategy_name == "Riemann":
        return Riemann()
    return Euclid()


def main() -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    selected_strategy = make_strategy(json_obj_list[0])
    tile_grid = make_tile_grid(json_obj_list[1]['board'])
    spare = make_individual_tile(json_obj_list[1]['spare'])
    board = Board(tile_grid, spare)
    goal_position = Position(json_obj_list[2]["row#"], json_obj_list[2]["column#"])
    observable_state = ObservableState(board)
    active_player = make_player_with_all_information(dict(json_obj_list[1]['plmt'][0]),
                                                     selected_strategy, goal_position)
    proposed_move = active_player.take_turn(observable_state)
    formatted_move = proposed_move.format_output()
    json_move = json.dumps(formatted_move)
    json_move_no_spaces = json_move.replace(' ', '')
    return json_move_no_spaces


# Entry point main method
if __name__ == '__main__':
    print(main())
