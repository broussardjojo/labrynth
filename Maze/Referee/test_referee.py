# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name
import time
from functools import wraps
from pathlib import Path
from typing import Tuple, Optional, Callable, Any
from unittest.mock import MagicMock

import pytest

from Maze.Common.abstract_state import AbstractState
from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.gem import Gem
from Maze.Common.position import Position
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.shapes import TShaped
from Maze.Common.state import State
from Maze.Common.thread_utils import sleep_interruptibly
from Maze.Common.tile import Tile
from Maze.Common.utils import get_json_obj_list, shape_dict
from Maze.JSON.deserializers import get_tile_grid_from_json
from Maze.Players.api_player import LocalPlayer
from Maze.Players.euclid import Euclid
from Maze.Players.move import Move, Pass
from Maze.Players.riemann import Riemann
from Maze.Players.strategy import Strategy
from Maze.Referee.referee import Referee
from Maze.config import CONFIG


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


# This board has the following shape:
#   ["┬","┐","─","─","┐","└","┌"],
#   ["└","│","─","┘","┬","├","┴"],
#   ["─","│","│","┐","│","│","─"],
#   ["┐","│","│","┬","┬","├","┴"],
#   ["┤","─","│","┐","┐","└","│"],
#   ["┘","├","│","┬","┤","─","│"],
#   ["─","┴","└","┐","┘","┬","├"]
# It's spare tile is a "┬" shape
@pytest.fixture
def basic_seeded_board_two():
    path = Path(__file__).parent.parent / "Players/basicBoardTwo.json"
    with path.open(encoding="utf-8") as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board(get_tile_grid_from_json(json_obj_list[0]),
                     Tile(TShaped(0), Gem("red-spinel-square-emerald-cut"), Gem("amethyst")))


@pytest.fixture
def board_slow_riemann_win():
    connector_rows = [
        "───────",
        "└──────",
        "───────",
        "───────",
        "───────",
        "───────",
        "───────",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["┬"])


@pytest.fixture
def board_fully_connected():
    connector_rows = [
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
        "┼┼┼┼┼┼┼",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["┬"])


@pytest.fixture
def player_one():
    return RefereePlayerDetails.from_home_goal_color(Position(5, 1), Position(3, 1), "pink")


@pytest.fixture
def player_two():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 3), Position(5, 5), "red")


@pytest.fixture
def player_three():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 1), Position(1, 1), "black")


@pytest.fixture
def player_four():
    return RefereePlayerDetails.from_home_goal_color(Position(1, 1), Position(5, 3), "blue")


@pytest.fixture
def player_five():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 3), Position(1, 3), "yellow")


@pytest.fixture
def player_six():
    return RefereePlayerDetails.from_home_goal_color(Position(1, 5), Position(1, 1), "green")


@pytest.fixture
def referee_no_observer(monkeypatch):
    monkeypatch.setattr(CONFIG, "referee_method_call_timeout", 0.5)
    with Referee() as referee:
        yield referee


@pytest.fixture
def seeded_referee_no_observer(monkeypatch):
    monkeypatch.setattr(CONFIG, "referee_method_call_timeout", 0.5)
    with Referee(random_seed=9) as referee:
        yield referee


@pytest.fixture
def seeded_game_state(seeded_board, player_one, player_two, player_three):
    return State.from_board_and_players(seeded_board, [player_one, player_two, player_three])


@pytest.fixture
def seeded_game_state_two(seeded_board, player_three, player_four, player_two):
    return State.from_board_and_players(seeded_board, [player_two, player_three, player_four])


@pytest.fixture
def seeded_game_state_three(basic_seeded_board_two, player_one, player_two, player_three):
    return State.from_board_and_players(basic_seeded_board_two, [player_one, player_two, player_three])


@pytest.fixture
def seeded_game_state_four(basic_seeded_board_two, player_one, player_three, player_five):
    return State.from_board_and_players(basic_seeded_board_two, [player_one, player_three, player_five])


@pytest.fixture
def state_slow_riemann_win(board_slow_riemann_win, player_one, player_two, player_six):
    player_one.set_current_position(Position(0, 3))
    player_two.set_current_position(Position(0, 4))
    player_six.set_current_position(Position(0, 5))
    return State(board_slow_riemann_win,
                 [(0, Direction.LEFT)],
                 [player_one, player_two, player_six],
                 active_player_index=0)


@pytest.fixture
def state_fully_connected(board_fully_connected):
    return State.from_board_and_players(
        board_fully_connected,
        [
            RefereePlayerDetails.from_home_goal_color(Position(1, 1), Position(1, 1), "red"),
            RefereePlayerDetails.from_home_goal_color(Position(5, 5), Position(5, 1), "blue")
        ]
    )


@pytest.fixture
def state_fully_connected_headstart(board_fully_connected):
    return State.from_board_and_players(
        board_fully_connected,
        [
            # arg order is home, goal, current
            RefereePlayerDetails(Position(1, 1), Position(1, 1), Position(1, 2), "red"),
            RefereePlayerDetails(Position(5, 5), Position(5, 1), Position(5, 5), "blue")
        ]
    )


# def with_config_overrides(**config_overrides):
#     def decorator(fn):
#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             config_originals = {}
#             for config_key, override_config_value in config_overrides.items():
#                 config_originals[config_key] = getattr(CONFIG, config_key)
#                 setattr(CONFIG, config_key, override_config_value)
#             result = fn(*args, **kwargs)
#             for config_key, original_config_value in config_originals.items():
#                 setattr(CONFIG, config_key, original_config_value)
#             return result
#         return wrapper
#     return decorator


class ForeverStrategy(Strategy):
    __alive = True

    def generate_move(self, current_state: AbstractState, target_position: Position) -> Move:
        while self.__alive:
            time.sleep(1)
        return Move(0, Direction.UP, 0, Position(2, 0))

    def wakeup(self):
        self.__alive = False


class BadSlideIndexStrategy(Strategy):
    def generate_move(self, current_state: AbstractState, target_position: Position) -> Move:
        return Move(1, Direction.UP, 90, Position(2, 0))


class BadMoveToStrategy(Strategy):
    def generate_move(self, current_state: AbstractState, target_position: Position) -> Move:
        return Move(0, Direction.UP, 90, Position(2, 0))


class BadRotationStrategy(Strategy):
    def generate_move(self, current_state: AbstractState, target_position: Position) -> Move:
        return Move(0, Direction.UP, 14, Position(2, 0))


class AlwaysPassStrategy(Strategy):

    def generate_move(self, current_state: AbstractState, target_position: Position) -> Pass:
        return Pass()


class AlwaysRaiseStrategy(Strategy):

    def generate_move(self, current_state: AbstractState, target_position: Position) -> Pass:
        a = 1 // 0
        return Pass()


# ----- Test referee without observer ------

# ----- Test run_game_from_state -------
def api_player_with_mock(player_name: str,
                         player_strategy: Strategy,
                         mocked_method_name: str,
                         implementation: Optional[Callable[..., Any]] = None) -> Tuple[LocalPlayer, MagicMock]:
    api_player = LocalPlayer(player_name, player_strategy)
    impl = implementation if implementation else getattr(api_player, mocked_method_name)
    mock = MagicMock(wraps=impl)
    setattr(api_player, mocked_method_name, mock)
    return api_player, mock


def test_run_game_all_pass(referee_no_observer, seeded_game_state_three, player_one, player_two, player_three):
    player_one.set_current_position(Position(5, 5))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    api_players, mocks = [], []
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", AlwaysPassStrategy(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == [api_players[1]]
    assert cheating_players == []
    for mock in mocks:
        assert mock.call_count == 1


@pytest.mark.parametrize("strategy_class", [BadMoveToStrategy, BadRotationStrategy, BadSlideIndexStrategy,
                                            AlwaysRaiseStrategy])
def test_run_game_all_cheaters(referee_no_observer, seeded_game_state_three, strategy_class):
    api_players, mocks = [], []
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", strategy_class(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == []
    assert cheating_players == api_players
    for mock in mocks:
        assert mock.call_count == 1


def test_run_game_all_timeout(referee_no_observer, seeded_game_state_three):
    api_players, mocks = [], []
    strategies = [ForeverStrategy(), ForeverStrategy(), ForeverStrategy()]
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", strategies[i], "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == []
    assert cheating_players == api_players
    for mock in mocks:
        assert mock.call_count == 1
    for strategy in strategies:
        strategy.wakeup()


def test_run_game_one_timeout(referee_no_observer, seeded_game_state_three):
    api_players, mocks = [], []
    strategies = [ForeverStrategy(), Riemann(), Euclid()]
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", strategies[i], "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == [api_players[2]]
    assert cheating_players == [api_players[0]]
    assert mocks[0].call_count == 1
    assert mocks[1].call_count == 2
    assert mocks[2].call_count == 2
    strategies[0].wakeup()


def test_run_game_one_safety_exception(referee_no_observer, seeded_game_state_three):
    api_players, mocks = [], []
    strategies = [Riemann(), AlwaysRaiseStrategy(), Euclid()]
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", strategies[i], "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == [api_players[0]]
    assert cheating_players == [api_players[1]]
    assert mocks[0].call_count == 2
    assert mocks[1].call_count == 1
    assert mocks[2].call_count == 1


def test_run_game_one_timeout_setup(referee_no_observer, seeded_game_state_three):
    api_players, mocks = [], []
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}",
                                                AlwaysPassStrategy(),
                                                "setup",
                                                (lambda *args: sleep_interruptibly(1)) if i == 0 else None)
        api_players.append(api_player)
        mocks.append(mock)
    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, seeded_game_state_three)
    assert winning_players == [api_players[2]]
    assert cheating_players == [api_players[0]]
    for mock in mocks:
        assert mock.call_count == 1


def test_run_game_all_valid_players(referee_no_observer, state_slow_riemann_win):
    api_players, mocks = [], []
    for i in range(3):
        api_player, mock = api_player_with_mock(f"player{i}", Riemann(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, state_slow_riemann_win)

    # tee gets inserted on turn 0 into (row 0, col 6) then moves left once per turn
    # col(tee) = (6 - turn_counter) % 8
    # if col(tee) is 7 that means it's on the spare tile
    # player_six is api_players[2], they get to their goal if col(tee) is 0, and turn % 3 == 2
    # player_six gets to their goal on turn index 14 (last of round 5),
    #   and then their home on turn index 17 (last of round 6)
    assert winning_players == [api_players[2]]
    assert cheating_players == []
    assert mocks[0].call_count == 6
    assert mocks[1].call_count == 6
    assert mocks[2].call_count == 6


def test_run_game_all_valid_players_player_one_goal_on_player_one_home(referee_no_observer, state_fully_connected):
    api_players, mocks = [], []
    for i in range(2):
        api_player, mock = api_player_with_mock(f"player{i}", Euclid(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, state_fully_connected)

    # player1 can win in 4 moves: (1,1) -> (0,1) -> goal(1,1) -> (0,1) -> home(1,1)
    # player2 should win in 2: (5,5) -> goal(5,1) -> home(5,5)
    assert winning_players == [api_players[1]]
    assert cheating_players == []
    assert mocks[0].call_count == 2
    assert mocks[1].call_count == 2
    assert state_fully_connected.get_players()[0].get_current_position() == Position(1, 1)
    assert state_fully_connected.get_players()[1].get_current_position() == Position(5, 5)


def test_run_game_all_valid_players_player_one_goal_on_player_one_home_variant(referee_no_observer,
                                                                               state_fully_connected_headstart):
    api_players, mocks = [], []
    for i in range(2):
        api_player, mock = api_player_with_mock(f"player{i}", Euclid(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players,
                                                                                state_fully_connected_headstart)

    # player1 can win in 3 moves: (1,2) -> goal(1,1) -> (0,1) -> home(1,1)
    # player2 should win in 2: (5,5) -> goal(5,1) -> home(5,5)
    assert winning_players == [api_players[1]]
    assert cheating_players == []
    assert mocks[0].call_count == 2
    assert mocks[1].call_count == 2
    # player1 moved to (0,1) but was shifted left by player2
    assert state_fully_connected_headstart.get_players()[0].get_current_position() == Position(0, 0)
    assert state_fully_connected_headstart.get_players()[1].get_current_position() == Position(5, 5)
