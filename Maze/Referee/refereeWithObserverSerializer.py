import json
from typing import List

from ..Players.player import Player
from .referee import Referee
from .refereeSerializer import make_state_from_json


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


def sort_winners(winners: List[Player]) -> List[str]:
    names = []
    for player in winners:
        names.append(player.get_name())
    names.sort()
    return names


# Entry point main method
if __name__ == '__main__':
    print(main())
