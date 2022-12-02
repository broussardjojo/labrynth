import functools
import io
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Set, List, Union, Tuple
from unittest.mock import MagicMock

import ijson
import pytest
from pydantic import ValidationError

from Maze.Common.thread_utils import gather_protected, sleep_interruptibly
from Maze.Common.utils import is_valid_player_name
from Maze.Server.server import Server, InvalidNameError
from Maze.Server.signup_state import SignupState, CancelledPhase, TimingEvent, CompletedHandshakeEvent, \
    WaitingPeriodPhase, RunGamePhase
from Maze.config import CONFIG

TESTING_PORT = 18765
SERVER_STOP_SENTINEL = object()


class StopsAfterTimedOutHandshakeServer(Server):

    def _handle_timed_out_handshake(self, connection: socket.socket) -> None:
        super()._handle_timed_out_handshake(connection)
        self._state = SignupState(phase=CancelledPhase(), players=self._state.players)


class StopsAfterInvalidHandshakeServer(Server):

    def _handle_invalid_handshake(self, connection: socket.socket, exception: Exception) -> None:
        super()._handle_invalid_handshake(connection, exception)
        self._state = SignupState(phase=CancelledPhase(), players=self._state.players)


def client(port_num: int, sends: Optional[bytes] = None, waits: float = 0) -> None:
    sleep_interruptibly(waits + 0.5)
    with socket.create_connection(("127.0.0.1", port_num)) as connection:
        if sends:
            connection.send(sends)
        connection.recv(1)


def good(name: str, waits: float):
    assert is_valid_player_name(name)
    return functools.partial(client, sends=json.dumps(name).encode("utf-8"), waits=waits)


def misnamed(name: str, waits: float):
    assert not is_valid_player_name(name)
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


@pytest.mark.parametrize("handshake_bytes", [
    b"}",
    b"mario",
    b"'mario'",
])
def test_failed_handshake_invalid_json(monkeypatch, handshake_bytes):
    server = Server(TESTING_PORT)
    with pytest.raises(ijson.IncompleteJSONError):
        server.handshake(io.BytesIO(handshake_bytes))


@pytest.mark.parametrize("handshake_json", [
    {"name": "mario"},
    ["luigi"],
    None,
    -1,
])
def test_failed_handshake_validation_error(monkeypatch, handshake_json):
    server = Server(TESTING_PORT)
    with pytest.raises(ValidationError):
        server.handshake(io.BytesIO(json.dumps(handshake_json).encode("utf-8")))


@pytest.mark.parametrize("handshake_json", [
    "spaced out",
    "D'Angelo",
    "0123456789o123456789o",
    "",
    "🥺"
])
def test_failed_handshake_invalid_name_error(monkeypatch, handshake_json):
    server = Server(TESTING_PORT)
    with pytest.raises(InvalidNameError):
        server.handshake(io.BytesIO(json.dumps(handshake_json).encode("utf-8")))


@pytest.mark.parametrize("handshake_json", [
    "i",
    "DAngelo",
    "0123456789o123456789",
])
def test_successful_handshake(monkeypatch, handshake_json):
    server = Server(TESTING_PORT)
    assert server.handshake(io.BytesIO(json.dumps(handshake_json).encode("utf-8"))) == handshake_json


"""SignupState but List[SafeAPIPlayer] is mapped to just the names."""
AbbreviatedSignupState = Tuple[Union[WaitingPeriodPhase, RunGamePhase, CancelledPhase], List[str]]


def signup_states(state0: SignupState, actions: List[Union[str, float]]) -> List[AbbreviatedSignupState]:
    result = [(state0.phase, [p.name() for p in state0.players])]
    state = state0
    for action in actions:
        if isinstance(action, str):
            mock_safe_api_player = MagicMock()
            mock_safe_api_player.name = MagicMock(return_value=action)
            state = Server.update_signup_state(state, CompletedHandshakeEvent(mock_safe_api_player))
        else:
            state = Server.update_signup_state(state, TimingEvent(action))
        result.append((state.phase, [p.name() for p in state.players]))
    return result


def test_update_signup_state_max_players_in_first_waiting_period():
    actions = [
        "adam",
        "bob",
        "charlie",
        "dylan",
        "eric",
        "fred",
        "gabrielle"
    ]
    assert signup_states(SignupState(phase=WaitingPeriodPhase(0), players=[]), actions) == [
        (WaitingPeriodPhase(0), []),
        (WaitingPeriodPhase(0), ["adam"]),
        (WaitingPeriodPhase(0), ["adam", "bob"]),
        (WaitingPeriodPhase(0), ["adam", "bob", "charlie"]),
        (WaitingPeriodPhase(0), ["adam", "bob", "charlie", "dylan"]),
        (WaitingPeriodPhase(0), ["adam", "bob", "charlie", "dylan", "eric"]),
        (RunGamePhase(), ["adam", "bob", "charlie", "dylan", "eric", "fred"]),
        # gabrielle not added
        (RunGamePhase(), ["adam", "bob", "charlie", "dylan", "eric", "fred"]),
    ]


def test_update_signup_state_max_players_in_second_waiting_period():
    actions = [
        "adam",
        19,
        19.5,
        20,
        "bob",
        "charlie",
        "dylan",
        "eric",
        "fred",
        "gabrielle"
    ]
    assert signup_states(SignupState(phase=WaitingPeriodPhase(0), players=[]), actions) == [
        (WaitingPeriodPhase(0), []),
        (WaitingPeriodPhase(0), ["adam"]),
        (WaitingPeriodPhase(0), ["adam"]),  # at 19s
        (WaitingPeriodPhase(0), ["adam"]),  # at 19.5s
        (WaitingPeriodPhase(1), ["adam"]),  # at 20s
        (WaitingPeriodPhase(1), ["adam", "bob"]),
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie"]),
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie", "dylan"]),
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie", "dylan", "eric"]),
        (RunGamePhase(), ["adam", "bob", "charlie", "dylan", "eric", "fred"]),
        # gabrielle not added
        (RunGamePhase(), ["adam", "bob", "charlie", "dylan", "eric", "fred"]),
    ]


def test_update_signup_state_min_players_by_first_waiting_period():
    actions = [
        "adam",
        "bob",
        19,
        19.5,
        20,
        "charlie",
    ]
    assert signup_states(SignupState(phase=WaitingPeriodPhase(0), players=[]), actions) == [
        (WaitingPeriodPhase(0), []),
        (WaitingPeriodPhase(0), ["adam"]),
        (WaitingPeriodPhase(0), ["adam", "bob"]),
        (WaitingPeriodPhase(0), ["adam", "bob"]),  # at 19s
        (WaitingPeriodPhase(0), ["adam", "bob"]),  # at 19.5s
        (RunGamePhase(), ["adam", "bob"]),  # at 20s
        # charlie not added
        (RunGamePhase(), ["adam", "bob"]),
    ]


def test_update_signup_state_min_players_by_second_waiting_period():
    actions = [
        "adam",
        19,
        19.5,
        20,
        "bob",
        "charlie",
        39,
        39.5,
        40,
        "dylan"
    ]
    assert signup_states(SignupState(phase=WaitingPeriodPhase(0), players=[]), actions) == [
        (WaitingPeriodPhase(0), []),
        (WaitingPeriodPhase(0), ["adam"]),
        (WaitingPeriodPhase(0), ["adam"]),  # at 19s
        (WaitingPeriodPhase(0), ["adam"]),  # at 19.5s
        (WaitingPeriodPhase(1), ["adam"]),  # at 20s
        (WaitingPeriodPhase(1), ["adam", "bob"]),
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie"]),
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie"]),  # at 39s
        (WaitingPeriodPhase(1), ["adam", "bob", "charlie"]),  # at 39.5s
        (RunGamePhase(), ["adam", "bob", "charlie"]),  # at 40s
        # dylan not added
        (RunGamePhase(), ["adam", "bob", "charlie"]),
    ]


# === testing translation from client behavior to handling ===
def test_unresponsive_client_causes_time_out():
    server = StopsAfterTimedOutHandshakeServer(TESTING_PORT)
    mock = MagicMock(wraps=server._handle_timed_out_handshake)
    server._handle_timed_out_handshake = mock
    with ThreadPoolExecutor() as executor:
        client_tasks = [executor.submit(client, TESTING_PORT, sends=None)]
        try:
            start_time = time.time()
            server.conduct_game()
            assert mock.call_count == 1
            assert time.time() - start_time == pytest.approx(2, abs=1)
        finally:
            gather_protected(client_tasks, timeout_seconds=1, debug=True)


@pytest.mark.parametrize("exc_type, handshake_bytes", [
    *[(ijson.IncompleteJSONError, v)
      for v in [b"}", b"mario", b"'mario'"]],
    *[(ValidationError, json.dumps(v).encode("utf-8") + b" ")
      for v in [{"name": "mario"}, ["luigi"], None, -1]],
    *[(InvalidNameError, json.dumps(v).encode("utf-8") + b" ")
      for v in ["spaced out", "D'Angelo", "0123456789o123456789o", "", "🥺"]]
])
def test_misbehaving_client_gets_disconnected(exc_type, handshake_bytes):
    server = StopsAfterInvalidHandshakeServer(TESTING_PORT)
    mock = MagicMock(wraps=server._handle_invalid_handshake)
    server._handle_invalid_handshake = mock
    with ThreadPoolExecutor() as executor:
        client_tasks = [executor.submit(client, TESTING_PORT, sends=handshake_bytes)]
        try:
            start_time = time.time()
            server.conduct_game()
            assert mock.call_count == 1
            assert type(mock.call_args_list[0].args[1]) is exc_type
            assert time.time() - start_time < 1
        finally:
            gather_protected(client_tasks, timeout_seconds=1, debug=True)


@pytest.mark.parametrize("handshake_json", [
    "i",
    "DAngelo",
    "0123456789o123456789",
])
def test_behaving_client_gets_signed_up(monkeypatch, handshake_json):
    # Configuring server to immediately run when first player joins
    monkeypatch.setattr(CONFIG, "server_minimum_players_to_start", 1)
    monkeypatch.setattr(CONFIG, "server_maximum_players_to_start", 1)
    # Setting run_game method to bypass the referee and just say everyone wins
    server = Server(TESTING_PORT, lambda _referee, players: (players, []))
    mock = MagicMock(wraps=Server._update_for_completed_handshake)
    monkeypatch.setattr(Server, "_update_for_completed_handshake", mock)
    with ThreadPoolExecutor() as executor:
        client_tasks = [executor.submit(client, TESTING_PORT, sends=json.dumps(handshake_json).encode("utf-8"))]
        try:
            start_time = time.time()
            assert server.conduct_game() == ([handshake_json], [])
            assert mock.call_count == 1
            assert time.time() - start_time < 1
        finally:
            gather_protected(client_tasks, timeout_seconds=1, debug=True)


def test_players_given_to_run_game_are_ordered_youngest_to_oldest(monkeypatch):
    # Configuring server to immediately run when three players join
    monkeypatch.setattr(CONFIG, "server_maximum_players_to_start", 3)
    # Setting run_game method to bypass the referee and just say everyone wins
    server = Server(TESTING_PORT, lambda _referee, players: (players, []))
    names = ["adam", "bob", "charlie"]
    with ThreadPoolExecutor() as executor:
        client_tasks = [
            executor.submit(client, TESTING_PORT, waits=idx, sends=json.dumps(name).encode("utf-8"))
            for idx, name in enumerate(names)
        ]
        try:
            start_time = time.time()
            assert server.conduct_game() == (["charlie", "bob", "adam"], [])
            assert time.time() - start_time == pytest.approx(2, abs=1)
        finally:
            gather_protected(client_tasks, timeout_seconds=1, debug=True)
