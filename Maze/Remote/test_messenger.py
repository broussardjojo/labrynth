import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Any, Tuple
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from Maze.Common.board import Board
from Maze.Common.position import Position
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.state import State
from Maze.Common.utils import get_json_obj_list
from Maze.JSON.deserializers import get_tile_grid_from_json
from Maze.Players.api_player import APIPlayer, LocalPlayer
from Maze.Players.euclid import Euclid
from Maze.Players.riemann import Riemann
from Maze.Remote.dispatching_receiver import DispatchingReceiver
from Maze.Remote.messenger import Messenger


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
        return Board.from_list_of_tiles(get_tile_grid_from_json(json_obj_list[0]), seed=30)


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


def dispatching_receiver_with_mock_player(connection: socket.socket,
                                          **implementations: Callable[..., Any]) -> Tuple[DispatchingReceiver, MagicMock]:
    mock_player = MagicMock()
    for key, fn in implementations.items():
        mock_player.attach_mock(MagicMock(wraps=fn), key)
    receiver = DispatchingReceiver(mock_player, connection.makefile("rb", buffering=0),
                                   connection.makefile("wb", buffering=0))
    return receiver, mock_player


def dispatching_receiver_with_mock_serializer(api_player: APIPlayer,
                                              connection: socket.socket,
                                              implementation: Callable[[Any], Any]) -> Tuple[DispatchingReceiver, MagicMock]:
    receiver = DispatchingReceiver(api_player, connection.makefile("rb", buffering=0),
                                   connection.makefile("wb", buffering=0))
    mock_serializer = MagicMock(wraps=implementation)
    setattr(receiver, "_DispatchingReceiver__serialize_return_type", mock_serializer)
    return receiver, mock_serializer


def test_remote_call_setup(seeded_game_state):
    server_conn, client_conn = socket.socketpair()

    receiver, mock = dispatching_receiver_with_mock_player(client_conn, setup=lambda state, goal: "✓")
    messenger = Messenger(server_conn.makefile("rb", buffering=0), server_conn.makefile("wb", buffering=0))
    with ThreadPoolExecutor() as executor:
        client_task = executor.submit(receiver.listen_forever)
        goal = seeded_game_state.get_players()[0].get_goal_position()
        assert messenger.call("setup", (seeded_game_state.copy_redacted(), goal)) == "✓"
        server_conn.shutdown(socket.SHUT_RDWR)
        client_task.result(timeout=1)
    setup_mock: MagicMock = mock.setup
    assert setup_mock.call_count == 1
    assert setup_mock.call_args[0][0].get_board().get_tile_grid() == seeded_game_state.get_board().get_tile_grid()
    assert setup_mock.call_args[0][1] == Position(3, 1)
    server_conn.close()
    client_conn.close()


def test_remote_call_name_type_error(seeded_game_state, api_player_one):
    server_conn, client_conn = socket.socketpair()

    # A number is not a name
    receiver, mock = dispatching_receiver_with_mock_serializer(api_player_one, client_conn, lambda _: 0)
    messenger = Messenger(server_conn.makefile("rb", buffering=0), server_conn.makefile("wb", buffering=0))
    with ThreadPoolExecutor() as executor:
        client_task = executor.submit(receiver.listen_forever)
        with pytest.raises(ValidationError):
            messenger.call("name", ())
        server_conn.shutdown(socket.SHUT_RDWR)
        client_task.result(timeout=1)
    assert mock.call_count == 1
    server_conn.close()
    client_conn.close()

# test_remote_call_setup(State.from_board_and_players(Board.from_random_board(3, 3), [
#     RefereePlayerDetails.from_home_goal_color(Position(5, 1), Position(3, 1), "red")]))
