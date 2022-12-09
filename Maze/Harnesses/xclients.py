import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import cast, List, Set

from Maze.Client.client import Client
from Maze.Common.signal_listener import sigint_received_context
from Maze.Common.thread_utils import sleep_interruptibly, get_now_protected
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.definitions import JSONEventuallyBadPlayerSpec
from Maze.JSON.deserializers import get_api_player_list_from_bad_player_spec_json
from Maze.Players.api_player import APIPlayer
from Maze.config import CONFIG

log = logging.getLogger(__name__)


def play_game_thread(player: APIPlayer, host: str, port: int, delay: float) -> None:
    with sigint_received_context() as cancel_status:
        sleep_interruptibly(delay, breaker=cancel_status)
    with Client(host, port) as client:
        dispatching_receiver = client.register_for_game(player)
        dispatching_receiver.listen_forever()


def play_game(players: List[APIPlayer], host: str, port: int) -> None:
    with ThreadPoolExecutor(max_workers=32) as executor:
        future_set: Set[Future[None]] = set()

        for join_index, player in enumerate(players):
            delay = (join_index + 1) * CONFIG.client_start_interval
            future_set.add(executor.submit(play_game_thread, player, host, port, delay))

        while len(future_set):
            # Interruptible version of gather_protected
            for fut in list(future_set):
                status = get_now_protected(fut)
                if isinstance(status, BaseException):
                    log.info("play_game_thread raised exception", exc_info=status)
                    future_set.remove(fut)
                elif status.is_present:
                    log.info("play_game_thread completed normally")
                    future_set.remove(fut)

            # If there are still incomplete futures, give them some time to run
            if len(future_set):
                time.sleep(0.01)



def main(port: str, host: str = "127.0.0.1") -> None:
    json_obj_list = get_json_obj_list(sys.stdin.read().lstrip())
    assert len(json_obj_list) == 1

    json_bad_player_spec = cast(JSONEventuallyBadPlayerSpec, json_obj_list[0])
    players = get_api_player_list_from_bad_player_spec_json(json_bad_player_spec)
    play_game(players, host, int(port))


if __name__ == '__main__':
    main(*sys.argv[1:])
