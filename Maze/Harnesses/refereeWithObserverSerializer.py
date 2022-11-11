import json
from typing import List

from Maze.Players.player import Player
from Maze.Referee.referee import Referee
from .xgames import make_state_from_json, sort_winners


def main() -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    state = make_state_from_json()
    referee = Referee(True)
    winners, cheaters = referee.run_game(state)
    ordered_winners = sort_winners(winners)
    json_winners = json.dumps(ordered_winners)
    json_winners_no_spaces = json_winners.replace(' ', '')
    return json_winners_no_spaces


# Entry point main method
if __name__ == '__main__':
    print(main())
