import functools
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Set
from unittest.mock import MagicMock

import pytest

from .server import Server
from ..Common.test_thread_utils import delayed_identity
from ..Common.thread_utils import gather_protected


def client(port_num: int, sends: Optional[bytes] = None, waits: float = 0) -> None:
    delayed_identity(waits + 0.5, None)
    with socket.create_connection(("127.0.0.1", port_num)) as connection:
        if sends:
            connection.send(sends)
        connection.recv(1)


def good(name: str, waits: float):
    return functools.partial(client, sends=json.dumps(name).encode("utf-8"), waits=waits)


def badjson(waits: float):
    return functools.partial(client, sends=b"}", waits=waits)


def badtype(waits: float):
    return functools.partial(client, sends=json.dumps({"name": "me"}).encode("utf-8"), waits=waits)


def unresp(waits: float):
    return functools.partial(client, sends=None, waits=waits)


@dataclass
class Game:
    min_waiting_time: float
    max_waiting_time: float
    names: Set[str]


@pytest.mark.parametrize("configs, expected", [
    # Everybody good, all join immediately
    ([good("dylan", 0), good("thomas", 0), good("adam", 0), good("bob", 0), good("charlie", 0), good("david", 0)],
     Game(0, 3, {"dylan", "thomas", "adam", "bob", "charlie", "david"})),
    # Some unresponsive, all join immediately
    ([good("dylan", 0), unresp(0), good("adam", 0), good("bob", 0), unresp(0), good("david", 0)],
     Game(20, 23, {"dylan", "adam", "bob", "david"})),
    # Some bad, all join in first waiting period, some not immediately
    ([good("dylan", 6), unresp(0), badjson(0), good("bob", 0), unresp(0), badtype(2)],
     Game(20, 23, ["bob", "dylan"])),
    # Some bad, some join in first waiting period, some join in second waiting period
    ([good("dylan", 6), unresp(0), badjson(0), good("bob", 30), unresp(0), badtype(2)],
     Game(40, 43, ["dylan", "bob"])),
    # All good, some join in first waiting period, some join in second waiting period
    ([good("dylan", 6), good("bob", 30), good("thomas", 31), good("adam", 32), good("bob2", 33), good("charlie", 34),
      good("david", 35)],
     Game(34, 37, ["dylan", "bob", "thomas", "adam", "bob2", "charlie"])),
    # All bad, some join in first waiting period, some join in second waiting period
    ([unresp(4), unresp(0), badjson(0), good("bob 2", 30), unresp(0), badtype(2)],
     Game(40, 43, set())),
    # All but one bad, some join in first waiting period, some join in second waiting period
    ([unresp(4), unresp(0), badjson(0), good("bob", 30), unresp(0), badtype(2)],
     Game(40, 43, set()))
])
def test_remote_call_setup(configs, expected):
    port_num = 8765
    server = Server(port_num)
    server_mock = MagicMock(wraps=lambda players, _: (players, []))
    setattr(server, "_Server__run_game", server_mock)
    with ThreadPoolExecutor() as executor:
        start_time = time.time()
        client_tasks = [executor.submit(client_fn, port_num) for client_fn in configs]
        try:
            actual_names = server.conduct_game()[0]
            if isinstance(expected.names, set):
                actual_names = set(actual_names)
            assert actual_names == expected.names
            elapsed_time = time.time() - start_time
            assert expected.min_waiting_time <= elapsed_time <= expected.max_waiting_time
            if actual_names:
                assert server_mock.call_count == 1
            else:
                assert server_mock.call_count == 0
        finally:
            gather_protected(client_tasks, timeout_seconds=1, debug=True)

