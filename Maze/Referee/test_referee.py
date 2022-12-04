# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name
import time
from pathlib import Path
from typing import Tuple, Optional, Callable, Any, Union, List
from unittest.mock import MagicMock

import pytest

from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.gem import Gem
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.shapes import TShaped
from Maze.Common.state import State
from Maze.Common.test_board import board_to_unicode
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
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["┼"])


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


@pytest.fixture
def state_fully_connected_two(board_fully_connected):
    return State.from_board_and_players(
        board_fully_connected,
        [
            RefereePlayerDetails.from_home_goal_color(Position(1, 1), Position(1, 5), "red"),
            RefereePlayerDetails.from_home_goal_color(Position(5, 5), Position(5, 1), "blue"),
            RefereePlayerDetails.from_home_goal_color(Position(3, 3), Position(3, 5), "green")
        ]
    )


@pytest.fixture
def state_fully_connected_three(board_fully_connected):
    return State.from_board_and_players(
        board_fully_connected,
        [
            RefereePlayerDetails.from_home_goal_color(Position(1, 1), Position(1, 5), "red"),
            RefereePlayerDetails.from_home_goal_color(Position(5, 5), Position(5, 3), "blue")
        ]
    )


@pytest.fixture
def state_fully_connected_four(board_fully_connected):
    return State.from_board_and_players(
        board_fully_connected,
        [
            RefereePlayerDetails.from_home_goal_color(Position(1, 1), Position(1, 1), "red"),
            RefereePlayerDetails.from_home_goal_color(Position(5, 5), Position(5, 5), "blue")
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

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Move:
        while self.__alive:
            time.sleep(1)
        return Move(0, Direction.UP, 0, Position(2, 0))

    def wakeup(self):
        self.__alive = False


class BadSlideIndexStrategy(Strategy):
    def generate_move(self, current_state: RedactedState, target_position: Position) -> Move:
        return Move(1, Direction.UP, 90, Position(2, 0))


class BadMoveToStrategy(Strategy):
    def generate_move(self, current_state: RedactedState, target_position: Position) -> Move:
        return Move(0, Direction.UP, 90, Position(2, 0))


class BadRotationStrategy(Strategy):
    def generate_move(self, current_state: RedactedState, target_position: Position) -> Move:
        return Move(0, Direction.UP, 14, Position(2, 0))


class AlwaysPassStrategy(Strategy):

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Pass:
        return Pass()


class AlwaysRaiseStrategy(Strategy):

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Pass:
        a = 1 // 0
        return Pass()


class HardcodedStrategy(Strategy):

    def __init__(self, decisions: List[Union[Move, Pass]]):
        self.decisions = decisions

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Union[Move, Pass]:
        return self.decisions.pop(0)

class ConcatStrategy(Strategy):
    def __init__(self, strategies_and_turn_counts: List[Tuple[Strategy, int]]):
        self.strategies_and_turn_counts = [(s, c) for s, c in strategies_and_turn_counts if c > 0]

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Union[Move, Pass]:
        strategy, turns_remaining = self.strategies_and_turn_counts[0]
        if turns_remaining <= 1:
            self.strategies_and_turn_counts.pop(0)
        else:
            self.strategies_and_turn_counts[0] = (strategy, turns_remaining - 1)
        return strategy.generate_move(current_state, target_position)
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


def test_run_game_empty_additional_goals_player_one_goal_on_player_one_home(monkeypatch,
                                                                            referee_no_observer,
                                                                            state_fully_connected):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    monkeypatch.setattr(referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: [])
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


def test_run_game_empty_additional_goals_player_one_and_two_goal_on_home(monkeypatch,
                                                                         referee_no_observer,
                                                                         state_fully_connected_four):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    monkeypatch.setattr(CONFIG, "referee_max_rounds", 2)
    monkeypatch.setattr(referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: [])
    api_players, mocks = [], []
    for i in range(2):
        api_player, mock = api_player_with_mock(f"player{i}", Euclid(), "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, state_fully_connected_four)

    # player1 reaches goal in 2: (1,1) -> (0,1) -> goal(1,1)
    # player2 reaches goal in 2: (5,5) -> (4,5) -> goal(5,5)
    # The game ends
    assert winning_players == [api_players[0], api_players[1]]
    assert cheating_players == []
    assert mocks[0].call_count == 2
    assert mocks[1].call_count == 2
    assert state_fully_connected_four.get_players()[0].get_current_position() == Position(1, 1)
    assert state_fully_connected_four.get_players()[1].get_current_position() == Position(5, 5)
    assert state_fully_connected_four.get_players()[0].is_goal_ultimate()
    assert state_fully_connected_four.get_players()[1].is_goal_ultimate()


def test_run_game_empty_additional_goals_player_one_and_two_goal_on_home_variant(monkeypatch,
                                                                                 referee_no_observer,
                                                                                 state_fully_connected_four):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    monkeypatch.setattr(referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: [])
    api_players, mocks = [], []
    for i in range(2):
        # each player should make two moves correctly, and then pass once
        strategy = ConcatStrategy([(Euclid(), 2), (AlwaysPassStrategy(), 1)])
        api_player, mock = api_player_with_mock(f"player{i}", strategy, "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = referee_no_observer.run_game_from_state(api_players, state_fully_connected_four)

    # player1 reaches goal in 2: (1,1) -> (0,1) -> goal(1,1)
    # player2 reaches goal in 2: (5,5) -> (4,5) -> goal(5,5)
    # Both players pass, the game ends
    assert winning_players == [api_players[0], api_players[1]]
    assert cheating_players == []
    assert mocks[0].call_count == 3
    assert mocks[1].call_count == 3
    assert state_fully_connected_four.get_players()[0].get_current_position() == Position(1, 1)
    assert state_fully_connected_four.get_players()[1].get_current_position() == Position(5, 5)
    assert state_fully_connected_four.get_players()[0].is_goal_ultimate()
    assert state_fully_connected_four.get_players()[1].is_goal_ultimate()


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


def test_run_game_referee_constructs_state_large_board(referee_no_observer):
    api_players, mocks = [], []
    for i in range(17):
        api_player, mock = api_player_with_mock(f"player{i}", AlwaysPassStrategy(), "setup")
        api_players.append(api_player)
        mocks.append(mock)

    referee_no_observer.run_game(api_players)
    for mock in mocks:
        assert mock.call_count == 1
        state: RedactedState = mock.call_args_list[0].args[0]
        assert state.get_board().get_height() == 11
        assert state.get_board().get_width() == 11


def test_run_game_referee_constructs_state_overly_large_board(referee_no_observer):
    api_players, mocks = [], []
    for i in range(1250):
        api_player, mock = api_player_with_mock(f"player{i}", AlwaysPassStrategy(), "setup")
        api_players.append(api_player)
        mocks.append(mock)

    with pytest.raises(ValueError) as err:
        referee_no_observer.run_game(api_players)
    assert "there are only enough gems to create a board with" in str(err.value)

    for mock in mocks:
        assert mock.call_count == 0


def test_run_game_referee_constructs_state(monkeypatch, board_fully_connected, seeded_referee_no_observer):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    board_mock = MagicMock(return_value=board_fully_connected)
    monkeypatch.setattr(seeded_referee_no_observer, "get_proposed_board", board_mock)

    api_players, mocks = [], []
    for i in range(2):
        api_player, mock = api_player_with_mock(f"player{i}", Euclid(), "setup")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = seeded_referee_no_observer.run_game(api_players)
    initial_state: RedactedState = mocks[0].call_args_list[0].args[0]
    assert board_to_unicode(initial_state.get_board()) == (
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼"
    )

    # Players trade off reaching goals
    # player2 is told to return home after round 4, turn 2 (turn 8 overall)
    # player1 is told to return home after round 5, turn 1
    # player2 ends the game by returning home on round 5, turn 2 - this does not award a point
    # Score: (5 goals, positive distance to next) vs. (4 goals, zero distance to next)
    assert winning_players == [api_players[0]]
    assert mocks[0].call_count == 6
    assert mocks[1].call_count == 5

    # Other than homes, all assigned treasures should be unique
    player1_assigned_treasures = [setup_call.args[1] for setup_call in mocks[0].call_args_list[:-1]]
    player2_assigned_treasures = [setup_call.args[1] for setup_call in mocks[1].call_args_list[:-1]]
    all_assigned_treasures = player1_assigned_treasures + player2_assigned_treasures
    assert len(all_assigned_treasures) == 9
    assert len(set(all_assigned_treasures)) == 9


def test_run_game_from_state_more_api_players_than_state_players(state_fully_connected, referee_no_observer):
    api_players = [LocalPlayer("a", AlwaysRaiseStrategy()),
                   LocalPlayer("b", AlwaysRaiseStrategy()),
                   LocalPlayer("c", AlwaysRaiseStrategy()),
                   ]
    with pytest.raises(ValueError) as err:
        referee_no_observer.run_game_from_state(api_players, state_fully_connected)
    assert "Number of APIPlayers (3) does not match number of players" in str(err.value)


def test_run_game_from_state_fewer_api_players_than_state_players(state_fully_connected, referee_no_observer):
    with pytest.raises(ValueError) as err:
        referee_no_observer.run_game_from_state([LocalPlayer("a", AlwaysRaiseStrategy())], state_fully_connected)
    assert "Number of APIPlayers (1) does not match number of players" in str(err.value)


def test_run_game_with_additional_goals_two_player_tie(monkeypatch, board_fully_connected,
                                                       state_fully_connected_two, seeded_referee_no_observer):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    additional_goals_for_tie = [
        *(set(board_fully_connected.get_all_stationary_positions())
          - {player.get_goal_position() for player in state_fully_connected_two.get_players()}
          - {Position(1, 1)}),
        # If the last overall goal is (1,1) player 1 should be ON their home when player 2 ends the game
        Position(1, 1)
    ]
    monkeypatch.setattr(seeded_referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: additional_goals_for_tie)

    # Player1 has a ConcatStrategy that makes it skip once
    # Player2 can use a euler strategy
    # Player3 should get two goals and then dawdle
    api_players, mocks = [], []
    strategies = [ConcatStrategy([(AlwaysPassStrategy(), 1), (Euclid(), 100)]),
                  Euclid(),
                  ConcatStrategy([(Euclid(), 2), (AlwaysPassStrategy(), 100)])
    ]
    for idx, strategy in enumerate(strategies):
        api_player, mock = api_player_with_mock(f"player{idx}", strategy, "setup")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = seeded_referee_no_observer.run_game_from_state(api_players,
                                                                                       state_fully_connected_two)
    # from Maze.Referee.tk_observer import TkObserver
    # observer = TkObserver()
    # seeded_referee_no_observer.add_observer(observer)
    # game_outcome_future = seeded_referee_no_observer.executor.submit(seeded_referee_no_observer.run_game_from_state, api_players, state_fully_connected_two)
    # live_observers = [observer]
    # while len(live_observers):
    #     timer_start = time.time()
    #     for observer in live_observers:
    #         if not observer.update_gui():
    #             # Observer exited
    #             live_observers.remove(observer)
    #     time.sleep(max(0.0, timer_start + CONFIG.observer_update_interval - time.time()))
    # winning_players, cheating_players = game_outcome_future.result()
    initial_state: RedactedState = mocks[0].call_args_list[0].args[0]
    assert board_to_unicode(initial_state.get_board()) == (
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼"
    )

    # Round 1: Player[0] skips, Players[1:] get one goal and are assigned additional_goals[0], additional_goals[1]
    # Round 2: All players get a goal, and are assigned additional_goals[2], additional_goals[3], additional_goals[4]
    # Round 3: Player[0] gets a goal and is assigned additional_goals[5], which is (1,1)
    #          Player[1] gets a goal and is assigned to return home
    #          Player[2] skips
    # Round 4: Player[0] gets a goal and is assigned to return home, which is (1,1) - they are already there
    #          Player[1] returns home and ends the game with a final score of 3-3-2,
    #          with Player[0] and Player[1] 0 distance from their home.
    # The winner is Player[1], since they have 1) tied for the most goals, 2) tied for minimum distance to next goal,
    #          3) Ended the game with their move.
    assert winning_players == [api_players[1]]
    assert mocks[0].call_count == 4
    assert mocks[1].call_count == 4
    assert mocks[2].call_count == 3


@pytest.mark.parametrize("player1_num_goals_before_pass, player2_num_goals_before_pass", [(3, 3), (0, 1)])
def test_run_game_with_additional_goals_two_player_early_end(monkeypatch, board_fully_connected,
                                                             state_fully_connected_three, seeded_referee_no_observer,
                                                             player1_num_goals_before_pass,
                                                             player2_num_goals_before_pass):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    additional_goals_for_early_end = sorted(
        (set(board_fully_connected.get_all_stationary_positions())
         - {player.get_goal_position() for player in state_fully_connected_three.get_players()}),
        key=Position.get_position_tuple
    )
    # = [(1,1), (1,3), (3,1), (3,3), (3,5), (5,1), (5,5)]
    monkeypatch.setattr(seeded_referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: additional_goals_for_early_end)

    api_players, mocks = [], []
    for i, call_count_threshold in enumerate([player1_num_goals_before_pass, player2_num_goals_before_pass]):
        strategy = ConcatStrategy([(Euclid(), call_count_threshold), (AlwaysPassStrategy(), 1000)])
        api_player, mock = api_player_with_mock(f"player{i}", strategy, "setup")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = seeded_referee_no_observer.run_game_from_state(api_players,
                                                                                       state_fully_connected_three)
    initial_state: RedactedState = mocks[0].call_args_list[0].args[0]
    assert board_to_unicode(initial_state.get_board()) == (
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼"
    )

    # thresholds = (3, 3)
    #     Players trade off reaching goals
    #     player1 -> (1, 5) (1, 1) (3, 1)
    #     player2 -> (5, 3) (1, 3) (3, 3)
    #     both players pass in round 4
    #     Score: (3 goals, current=(3,1) next=(3,5)) vs. (3 goals, current=(3,3) next=(5,1))
    # thresholds = (0, 1)
    #     player1 PASS
    #     player2 -> (5, 3)
    #     both players pass in round 2
    #     Score: (0 goals, current=(1,1) next=(1,5)) vs. (1 goal, current=(5,3) next=(1,1))
    assert winning_players == [api_players[1]]
    assert mocks[0].call_count == player1_num_goals_before_pass + 1
    assert mocks[1].call_count == player2_num_goals_before_pass + 1


def test_run_game_with_additional_goals_game_terminating_player_loses(monkeypatch,
                                                                      board_fully_connected,
                                                                      state_fully_connected_three,
                                                                      seeded_referee_no_observer):
    monkeypatch.setattr(CONFIG, "referee_use_additional_goals", True)
    additional_goals_for_early_end = sorted(
        (set(board_fully_connected.get_all_stationary_positions())
         - {player.get_goal_position() for player in state_fully_connected_three.get_players()}),
        key=Position.get_position_tuple
    )
    # = [(1,1), (1,3), (3,1), (3,3), (3,5), (5,1), (5,5)]
    monkeypatch.setattr(seeded_referee_no_observer, "_Referee__generate_additional_goals_from_state",
                        lambda *args, **kwargs: additional_goals_for_early_end)

    api_players, mocks = [], []
    strategies = [
        # player[0] gets goals early, but taunts player[1] into ending the game
        ConcatStrategy([(Euclid(), 7), (AlwaysPassStrategy(), 1000)]),
        # player[1] passes early, then plays normally
        ConcatStrategy([(AlwaysPassStrategy(), 6), (Euclid(), 1000)]),
    ]
    for i, strategy in enumerate(strategies):
        api_player, mock = api_player_with_mock(f"player{i}", strategy, "take_turn")
        api_players.append(api_player)
        mocks.append(mock)

    winning_players, cheating_players = seeded_referee_no_observer.run_game_from_state(api_players,
                                                                                       state_fully_connected_three)
    initial_state: RedactedState = mocks[0].call_args_list[0].args[0]
    assert board_to_unicode(initial_state.get_board()) == (
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼\n"
        "┼┼┼┼┼┼┼"
    )

    # First player gets initial goal and all but 1 additional goal
    #     player[0] -> (1, 5) (1, 1) (1, 3) (3, 1) (3, 3) (3, 5) (5, 1) PASS...
    #     player[1] -> PASS   PASS   PASS   PASS   PASS   PASS   (5, 3) home(5, 5)
    #     round        |1     |2     |3     |4     |5     |6     |7     |8
    #
    # NOTE: (5, 5) is assigned to player[0] as a non-terminal goal but is never reached
    #     Score: (7 goals, current=(5,1) next=(5,5)) vs. (2 goals, current=(5,5) next=(5,5))
    assert winning_players == [api_players[0]]
    assert mocks[0].call_count == 8
    assert mocks[1].call_count == 8
    assert state_fully_connected_three.get_players()[0].get_current_position() == Position(5, 1)
    assert state_fully_connected_three.get_players()[1].get_current_position() == Position(5, 5)
    assert state_fully_connected_three.get_players()[0].get_goal_position() == Position(5, 5)
    assert state_fully_connected_three.get_players()[0].is_goal_ultimate() is False
