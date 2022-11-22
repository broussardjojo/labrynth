import json
import sys
from typing import cast, List, Tuple

from Maze.Server.server import Server
from ..Common.state import State
from ..Common.utils import get_json_obj_list
from ..JSON.definitions import JSONBadPlayerSpec, JSONRefereeState
from ..JSON.deserializers import get_api_player_list_from_bad_player_spec_json, get_state_from_json
from ..Players.api_player import APIPlayer
from ..Referee.referee import Referee


def run_game(players: List[APIPlayer], state: State) -> Tuple[List[str], List[str]]:
    """
    Uses a referee to compute the outcome of a game beginning with the given game state, involving the given APIPlayers.
    :param players: A list of APIPlayer instances
    :param state: A state for the referee to use
    :return: A tuple of two lists of strings; the first represents winners, and the second represents cheaters. Both
    lists are sorted in alphabetical order
    """
    with Referee() as referee:
        winners, cheaters = referee.run_game_from_state(players, state)
    winners_names = [player.name() for player in winners]
    cheaters_names = [player.name() for player in cheaters]
    winners_names.sort()
    cheaters_names.sort()
    return winners_names, cheaters_names


def main(port: str) -> Tuple[List[str], List[str]]:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 1
    json_referee_state = cast(JSONRefereeState, json_obj_list[0])
    state = get_state_from_json(json_referee_state)
    server = Server(int(port), lambda ref, players: ref.run_game_from_state(players, state))
    return server.conduct_game()


# Entry point main method
if __name__ == '__main__':
    json.dump(main(*sys.argv[1:]), sys.stdout)
    print()
