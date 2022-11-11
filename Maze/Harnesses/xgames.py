import json
import sys
from typing import List, cast

from Maze.Common.state import State
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.definitions import JSONPlayerSpec, JSONRefereeState
from Maze.JSON.deserializers import get_api_player_list_from_player_spec_json, \
    get_state_from_json_referee_state
from Maze.Players.api_player import APIPlayer
from Maze.Referee.referee import Referee


def run_game(players: List[APIPlayer], state: State) -> List[str]:
    """
    Uses a referee to compute the outcome of a game beginning with the given game state, involving the given APIPlayers.
    :param players: A list of APIPlayer instances
    :param state: A state for the referee to use
    :return: A lists of strings representing winners, which is sorted in alphabetical order
    """
    referee = Referee()
    winners, cheaters = referee.run_game_from_state(players, state)
    winners_names = [player.name() for player in winners]
    winners_names.sort()
    return winners_names

def main() -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 2
    json_bad_player_spec = cast(JSONPlayerSpec, json_obj_list[0])
    json_referee_state = cast(JSONRefereeState, json_obj_list[1])
    players = get_api_player_list_from_player_spec_json(json_bad_player_spec)
    state = get_state_from_json_referee_state(json_referee_state)
    winners_names = run_game(players, state)
    return json.dumps(winners_names)


# Entry point main method
if __name__ == '__main__':
    print(main())
