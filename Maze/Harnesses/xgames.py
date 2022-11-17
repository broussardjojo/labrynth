import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, cast

from Maze.Common.state import State
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.definitions import JSONPlayerSpec, JSONRefereeState
from Maze.JSON.deserializers import get_api_player_list_from_player_spec_json, \
    get_state_from_json
from Maze.Players.api_player import APIPlayer
from Maze.Referee.observer import Observer
from Maze.Referee.tk_observer import TkObserver
from Maze.Referee.referee import Referee


TARGET_OBSERVER_UPDATE_SPEED = 1 / 60


def run_game(players: List[APIPlayer], state: State, observers: List[Observer]) -> List[str]:
    """
    Uses a referee to compute the outcome of a game beginning with the given game state, involving the given APIPlayers.
    :param players: A list of APIPlayer instances
    :param state: A state for the referee to use
    :param observers: The observers to add to the referee
    :return: A lists of strings representing winners, which is sorted in alphabetical order
    """
    with ThreadPoolExecutor(max_workers=32) as executor:
        referee = Referee(executor=executor)
        for observer in observers:
            referee.add_observer(observer)
        game_outcome_future = executor.submit(referee.run_game_from_state, players, state)
        live_observers = observers.copy()
        while len(live_observers):
            timer_start = time.time()
            for observer in live_observers:
                if not observer.update_gui():
                    # Observer exited
                    live_observers.remove(observer)
            time.sleep(max(0.0, timer_start + TARGET_OBSERVER_UPDATE_SPEED - time.time()))
        winners, _ = game_outcome_future.result()
    winners_names = [player.name() for player in winners]
    winners_names.sort()
    return winners_names


def main(should_add_observer: bool) -> str:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :param should_add_observer: True if the user wants to observe the game's intermediate states, False otherwise
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 2
    json_bad_player_spec = cast(JSONPlayerSpec, json_obj_list[0])
    json_referee_state = cast(JSONRefereeState, json_obj_list[1])
    players = get_api_player_list_from_player_spec_json(json_bad_player_spec)
    state = get_state_from_json(json_referee_state)
    observers = [TkObserver()] if should_add_observer else []
    winners_names = run_game(players, state, observers)
    return json.dumps(winners_names)


# Entry point main method
if __name__ == '__main__':
    with_observer = "--with-observer" in sys.argv
    print(main(with_observer))
