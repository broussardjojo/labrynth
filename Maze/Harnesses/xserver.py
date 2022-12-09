import json
import sys
import time
from functools import partial
from typing import cast, List, Tuple

from Maze.Common.position import Position
from Maze.Common.state import State
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.definitions import JSONRefereeState2
from Maze.JSON.deserializers import get_state_and_goals_from_json
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Referee.referee import Referee, GameOutcome
from Maze.Referee.tk_observer import TkObserver
from Maze.Server.server import Server
from Maze.config import CONFIG


def run_game(state: State, additional_goals: List[Position], referee: Referee,
             players: List[SafeAPIPlayer]) -> GameOutcome:
    """
    Uses a referee to compute the outcome of a game beginning with the given game state,
    involving the given SafeAPIPlayers.
    :param state: A state for the referee to use
    :param referee: A referee
    :param players: A list of SafeAPIPlayer instances
    :return: The outcome of the game: (winners, cheaters)
    """
    return referee.run_game_with_safe_players_and_goals(players, state, additional_goals)


def run_with_observer(state: State, additional_goals: List[Position], referee: Referee,
                      players: List[SafeAPIPlayer]) -> GameOutcome:
    """
    Uses a referee to compute the outcome of a game beginning with the given game state, involving the given
    SafeAPIPlayers, and using an observer.
    :param state: A state for the referee to use
    :param referee: A referee
    :param players: A list of SafeAPIPlayer instances
    :return: The outcome of the game: (winners, cheaters)
    """
    observers = [TkObserver()]
    referee.add_observer(observers[0])
    game_task = referee.executor.submit(referee.run_game_with_safe_players_and_goals, players, state, additional_goals)
    live_observers = observers.copy()
    while len(live_observers):
        timer_start = time.time()
        for observer in live_observers:
            if not observer.update_gui():
                # Observer exited
                live_observers.remove(observer)
        time.sleep(max(0.0, timer_start + CONFIG.observer_update_interval - time.time()))
    return game_task.result()


def main(port: str, *options: str) -> Tuple[List[str], List[str]]:
    """
    Main method which composes many helper methods to read input, compute moves, get the reachable tiles, sort them,
     and encode output
    :return: A sorted list of coordinates
    """
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 1
    json_referee_state = cast(JSONRefereeState2, json_obj_list[0])
    state, additional_goals = get_state_and_goals_from_json(json_referee_state)
    if "--with-observer" in options:
        server = Server(int(port), partial(run_with_observer, state, additional_goals))
    else:
        server = Server(int(port), partial(run_game, state, additional_goals))
    winner_names, cheater_names = server.conduct_game()
    winner_names.sort()
    cheater_names.sort()
    return winner_names, cheater_names


# Entry point main method
if __name__ == '__main__':
    json.dump(main(*sys.argv[1:]), sys.stdout)
    print()
