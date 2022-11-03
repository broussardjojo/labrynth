import json
from typing import List

from ..Players.player import Player
from ..Referee.referee import Referee
from ..Common.state import State
from ..Common.utils import get_json_obj_list
from ..Common.boardSerializer import make_tile_grid, make_individual_tile
from ..Players.playerSerializer import make_list_of_players_given_info
from ..Common.board import Board
import sys


def main() -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    state = make_state_from_json()
    referee = Referee()
    winners, cheaters = referee.run_game(state)
    ordered_winners = sort_winners(winners)
    json_winners = json.dumps(ordered_winners)
    json_winners_no_spaces = json_winners.replace(' ', '')
    return json_winners_no_spaces


def make_state_from_json() -> State:
    """
    Makes a state from information provided by the given JSON input
    :return: a State which represents a state of a game of Labyrinth
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    tile_grid = make_tile_grid(json_obj_list[1]['board'])
    spare = make_individual_tile(json_obj_list[1]['spare'])
    board = Board(tile_grid, spare)
    list_of_players_and_strategies = list(json_obj_list[0])
    list_of_player_information = json_obj_list[1]['plmt']
    player_list = make_list_of_players_given_info(list_of_players_and_strategies, list_of_player_information)
    state = State.from_board_and_players(board, player_list)
    return state


def sort_winners(winners: List[Player]) -> List[str]:
    """
    Provides a list of names given a list of players, sorted in alphabetical order
    :param winners: represents a list of winning players
    :return: a list of the names from the given list of players sorted in alphabetical order
    """
    names = []
    for player in winners:
        names.append(player.get_name())
    names.sort()
    return names


# Entry point main method
if __name__ == '__main__':
    print(main())
