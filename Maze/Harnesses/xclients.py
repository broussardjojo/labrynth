import sys
from concurrent.futures import ThreadPoolExecutor, Future
from typing import cast, List

from Maze.Client.client import Client
from Maze.Common.thread_utils import gather_protected, sleep_interruptibly
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.definitions import JSONEventuallyBadPlayerSpec
from Maze.JSON.deserializers import get_api_player_list_from_bad_player_spec_json
from Maze.Players.api_player import APIPlayer
from Maze.config import CONFIG

# A timeout for the period of the game running.
# Given our 6 player 1000 turn limit, this should never be hit.
GAME_TIME_LIMIT_SECONDS = 100000


def play_game_thread(player: APIPlayer, host: str, port: int, delay: float) -> None:
    sleep_interruptibly(delay)
    with Client(host, port) as client:
        dispatching_receiver = client.register_for_game(player)
        dispatching_receiver.listen_forever()


def play_game(players: List[APIPlayer], host: str, port: int) -> None:
    with ThreadPoolExecutor(max_workers=32) as executor:
        future_list: List[Future[None]] = []

        for join_index, player in enumerate(reversed(players)):
            delay = join_index * CONFIG.client_start_interval
            future_list.append(executor.submit(play_game_thread, player, host, port, delay))

        gather_protected(
            future_list,
            timeout_seconds=GAME_TIME_LIMIT_SECONDS, debug=True
        )


def main(port: str, host: str = "127.0.0.1") -> None:
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 1

    json_bad_player_spec = cast(JSONEventuallyBadPlayerSpec, json_obj_list[0])
    players = get_api_player_list_from_bad_player_spec_json(json_bad_player_spec)
    play_game(players, host, int(port))


if __name__ == '__main__':
    main(*sys.argv[1:])
