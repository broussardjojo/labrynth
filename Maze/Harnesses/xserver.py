import json
import sys
import time
from typing import cast, List, Tuple

from Maze.Common.state import State
from Maze.Common.utils import get_json_obj_list
from Maze.Harnesses.xgames import TARGET_OBSERVER_UPDATE_SPEED
from Maze.JSON.definitions import JSONRefereeState
from Maze.JSON.deserializers import get_state_from_json
from Maze.Players.api_player import APIPlayer
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Referee.referee import Referee, GameOutcome
from Maze.Referee.tk_observer import TkObserver
from Maze.Server.server import Server


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


def run_with_observers(state: State, ref: Referee, players: List[SafeAPIPlayer]) -> GameOutcome:
    observers = [TkObserver()]
    ref.add_observer(observers[0])
    game_task = ref.executor.submit(ref.run_game_with_safe_players_from_state, players, state)
    live_observers = observers.copy()
    while len(live_observers):
        timer_start = time.time()
        for observer in live_observers:
            if not observer.update_gui():
                # Observer exited
                live_observers.remove(observer)
        time.sleep(max(0.0, timer_start + TARGET_OBSERVER_UPDATE_SPEED - time.time()))
    return game_task.result()


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
    server = Server(int(port), lambda ref, players: ref.run_game_with_safe_players_from_state(players, state))
    # server = Server(int(port), partial(run_with_observers, state))
    return server.conduct_game()


# Entry point main method
if __name__ == '__main__':
    json.dump(main(*sys.argv[1:]), sys.stdout)
    print()
