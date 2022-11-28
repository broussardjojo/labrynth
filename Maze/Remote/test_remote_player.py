import contextlib
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Any, Tuple
from unittest.mock import MagicMock

import ijson
import pytest
from pydantic import ValidationError

from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.gem import Gem
from Maze.Common.position import Position
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.shapes import TShaped
from Maze.Common.state import State
from Maze.Common.thread_utils import await_protected
from Maze.Common.tile import Tile
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.deserializers import get_tile_grid_from_json
from Maze.Players.api_player import LocalPlayer
from Maze.Players.euclid import Euclid
from Maze.Players.move import Move, Pass
from Maze.Players.riemann import Riemann
from Maze.Remote.referee import DispatchingReceiver
from Maze.Remote.remote_player_methods import RemotePlayerMethods
from Maze.Remote.player import RemotePlayer


# ----- Examples ------
# This board has the following shape:
#   ["┬","┐","─","─","┐","└","┌"],
#   ["└","│","─","┘","┬","├","┴"],
#   ["─","│","│","┐","│","│","─"],
#   ["┐","│","─","┬","┬","├","┴"],
#   ["┤","┼","│","┐","┐","└","│"],
#   ["┘","├","│","┬","┤","┼","│"],
#   ["─","┴","└","┐","┘","┬","├"]
# It's spare tile is a "┬" shape
@pytest.fixture
def seeded_board():
    path = Path(__file__).parent.parent / "Players/basicBoard.json"
    with path.open(encoding="utf-8") as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board(get_tile_grid_from_json(json_obj_list[0]),
                     Tile(TShaped(0), Gem("red-spinel-square-emerald-cut"), Gem("amethyst")))


@pytest.fixture
def player_one():
    return RefereePlayerDetails.from_home_goal_color(Position(5, 1), Position(3, 1), "pink")


@pytest.fixture
def player_two():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 3), Position(5, 5), "red")


@pytest.fixture
def seeded_game_state(seeded_board, player_one, player_two):
    return State.from_board_and_players(seeded_board, [player_one, player_two])


@pytest.fixture
def api_player_one():
    return LocalPlayer("player1", Riemann())


@pytest.fixture
def api_player_two():
    return LocalPlayer("player2", Euclid())


@pytest.fixture
def socketpair():
    pair = socket.socketpair()
    try:
        yield pair
    finally:
        pair[0].close()
        pair[1].close()

SocketPairType = Tuple[socket.socket, socket.socket]

@contextlib.contextmanager
def ensure_shutdown(connection: socket.socket):
    try:
        yield
    finally:
        connection.shutdown(socket.SHUT_RDWR)


def dispatching_receiver_with_mock_player(connection: socket.socket,
                                          **implementations: Callable[..., Any]) -> Tuple[DispatchingReceiver, MagicMock]:
    mock_player = MagicMock()
    for key, fn in implementations.items():
        mock_player.attach_mock(MagicMock(wraps=fn), key)
    receiver = DispatchingReceiver.from_socket(mock_player, connection)
    return receiver, mock_player


def test_remote_call_setup(socketpair: SocketPairType, seeded_game_state):
    server_conn, client_conn = socketpair

    receiver, mock = dispatching_receiver_with_mock_player(client_conn, setup=lambda state, goal: "✓")
    remote_player = RemotePlayer.from_socket("player1", server_conn)
    with ThreadPoolExecutor() as executor:
        with ensure_shutdown(server_conn):
            client_task = executor.submit(receiver.listen_forever)
            goal = seeded_game_state.get_players()[0].get_goal_position()
            assert remote_player.setup(seeded_game_state.copy_redacted(), goal) == "void"
        await_protected(client_task, timeout_seconds=1)
    setup_mock: MagicMock = mock.setup
    assert setup_mock.call_count == 1
    assert setup_mock.call_args[0][0].get_board().get_tile_grid() == seeded_game_state.get_board().get_tile_grid()
    assert setup_mock.call_args[0][1] == Position(3, 1)


@pytest.mark.parametrize("did_win", [
    True,
    False
])
def test_remote_call_win(socketpair: SocketPairType, did_win):
    server_conn, client_conn = socketpair

    receiver, mock = dispatching_receiver_with_mock_player(client_conn, win=lambda w: "✓")
    remote_player = RemotePlayer.from_socket("player1", server_conn)
    with ThreadPoolExecutor() as executor:
        with ensure_shutdown(server_conn):
            client_task = executor.submit(receiver.listen_forever)
            assert remote_player.win(did_win) == "void"
        await_protected(client_task, timeout_seconds=1)
    win_mock: MagicMock = mock.win
    assert win_mock.call_count == 1
    assert win_mock.call_args[0][0] is did_win


@pytest.mark.parametrize("choice", [
    0,
    "pass",
    [],
    {},
    [0.5, "UP", 90, {"row#": 0, "column#": 0}],
    [0, "up", 90, {"row#": 0, "column#": 0}],
    [0, "UP", -90, {"row#": 0, "column#": 0}],
    [0, "UP", 90, {"row": 0, "column": 0}],
    [0, "UP", 90, {"row#": 0, "column#": 0}, None],
])
def test_remote_call_take_turn_type_error(socketpair: SocketPairType, seeded_game_state, monkeypatch, choice):
    server_conn, client_conn = socketpair

    # Ensure that the Player.take_turn() result is passed directly to json.dumps
    monkeypatch.setattr(RemotePlayerMethods.take_turn, "_RemotePlayerMethod__serialize_result", lambda x: x)

    receiver, mock = dispatching_receiver_with_mock_player(client_conn, take_turn=lambda state: choice)
    remote_player = RemotePlayer.from_socket("player1", server_conn)
    with ThreadPoolExecutor() as executor:
        with ensure_shutdown(server_conn):
            client_task = executor.submit(receiver.listen_forever)
            goal = seeded_game_state.get_players()[0].get_goal_position()
            assert remote_player.setup(seeded_game_state.copy_redacted(), goal) == "void"
            with pytest.raises(ValidationError):
                remote_player.take_turn(seeded_game_state.copy_redacted())
        await_protected(client_task, timeout_seconds=1)

    take_turn_mock: MagicMock = mock.take_turn
    assert take_turn_mock.call_count == 1


@pytest.mark.parametrize("output", [
    Move(0, Direction.UP, 90, Position(1, 2)),
    Move(0, Direction.DOWN, 0, Position(5, 2)),
    Move(1000, Direction.RIGHT, 180, Position(5555, 2)),
    Move(1, Direction.LEFT, 270, Position(0, 0)),
    Pass()
])
def test_remote_call_win(socketpair: SocketPairType, seeded_game_state, output):
    server_conn, client_conn = socketpair

    receiver, mock = dispatching_receiver_with_mock_player(client_conn, take_turn=lambda w: output)
    remote_player = RemotePlayer.from_socket("player1", server_conn)
    with ThreadPoolExecutor() as executor:
        with ensure_shutdown(server_conn):
            client_task = executor.submit(receiver.listen_forever)
            assert remote_player.take_turn(seeded_game_state.copy_redacted()) == output
        await_protected(client_task, timeout_seconds=1)
    take_turn_mock: MagicMock = mock.take_turn
    assert take_turn_mock.call_count == 1
    assert take_turn_mock.call_args[0][0].get_board().get_tile_grid() == seeded_game_state.get_board().get_tile_grid()


@pytest.mark.parametrize("malformed", [
    b'}',
    b'{{',
    b']',
    b'////',
    b'))o)',
    b"[0, 'UP', -90, {'row#': 0, 'column#': 0}]",
    b",",
    b"&~`"
])
def test_remote_call_take_turn_malformed_json(socketpair: SocketPairType, seeded_game_state, monkeypatch, malformed):
    server_conn, client_conn = socketpair
    remote_player = RemotePlayer.from_socket("player1", server_conn)
    receiver, mock = dispatching_receiver_with_mock_player(client_conn, take_turn=lambda state: Pass())
    write_channel = getattr(receiver, "_DispatchingReceiver__write_channel")
    original_write = write_channel.write
    monkeypatch.setattr(write_channel, "write", lambda *args: original_write(malformed))

    with ThreadPoolExecutor() as executor:
        with ensure_shutdown(server_conn):
            client_task = executor.submit(receiver.listen_forever)
            with pytest.raises(ijson.IncompleteJSONError):
                remote_player.take_turn(seeded_game_state.copy_redacted())
        await_protected(client_task, timeout_seconds=1)

    take_turn_mock: MagicMock = mock.take_turn
    assert take_turn_mock.call_count == 1
