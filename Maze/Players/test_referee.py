import time
from pathlib import Path

import pytest

from .euclid import Euclid
from .move import Move
from .player import Player
from .referee import Referee
from .riemann import Riemann
from .strategy import Strategy
from ..Common.board import Board
from ..Common.boardSerializer import make_tile_grid
from ..Common.observableState import ObservableState
from ..Common.position import Position
from ..Common.utils import get_json_obj_list
from ..Common.state import State


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
    path = Path(__file__).parent / "basicBoard.json"
    with path.open() as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board.from_list_of_tiles(make_tile_grid(json_obj_list[0]), seed=30)


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
    path = Path(__file__).parent / "basicBoardTwo.json"
    with path.open() as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board.from_list_of_tiles(make_tile_grid(json_obj_list[0]), seed=30)


@pytest.fixture
def player_one():
    return Player.from_goal_home_color_strategy(Position(3, 1), Position(5, 1), "pink", Riemann())


@pytest.fixture
def player_two():
    return Player.from_goal_home_color_strategy(Position(5, 5), Position(3, 3), "red", Riemann())


@pytest.fixture
def player_three():
    return Player.from_goal_home_color_strategy(Position(1, 1), Position(3, 1), "black", Euclid())


@pytest.fixture
def player_four():
    return Player.from_goal_home_color_strategy(Position(5, 3), Position(1, 1), "blue", Euclid())


@pytest.fixture
def seeded_game_state(seeded_board, player_one, player_two, player_three):
    return State.from_board_and_players(seeded_board, [player_one, player_two, player_three])


@pytest.fixture
def seeded_game_state_two(seeded_board, player_three, player_four, player_two):
    return State.from_board_and_players(seeded_board, [player_two, player_three, player_four])


@pytest.fixture
def seeded_game_state_three(basic_seeded_board_two, player_one, player_two, player_three):
    return State.from_board_and_players(basic_seeded_board_two, [player_one, player_two, player_three])


class ForeverStrategy(Strategy):

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        while True:
            time.sleep(1)
        return Move(0, Direction.Up, 0, Position(2, 0), False)


@pytest.fixture
def forever_strategy():
    return ForeverStrategy()


@pytest.fixture
def referee():
    return Referee()


@pytest.fixture
def player_forever(forever_strategy):
    return Player.from_goal_home_color_strategy(Position(1, 5), Position(3, 1), "green", forever_strategy)


@pytest.fixture
def game_state_with_forever_player(seeded_board, player_forever, player_two, player_three, player_four):
    return State.from_board_and_players(seeded_board, [player_forever, player_two, player_three, player_four])


@pytest.fixture
def game_state_with_forever_player_two(basic_seeded_board_two, player_forever, player_two, player_three, player_four):
    return State.from_board_and_players(basic_seeded_board_two, [player_forever, player_two, player_three, player_four])


# ----- Test run_game -------
def test_run_game_results_one(referee, seeded_game_state, player_one):
    winning_players, cheating_players = referee.run_game(seeded_game_state)
    assert winning_players == [player_one]
    assert cheating_players == []


def test_run_game_results_two(referee, seeded_game_state_two, player_three):
    winning_players, cheating_players = referee.run_game(seeded_game_state_two)
    assert winning_players == [player_three]
    assert cheating_players == []


def test_run_game_all_pass(referee, seeded_game_state_three, player_one, player_two, player_three):
    player_one.set_current_position(Position(5, 5))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    winning_players, cheating_players = referee.run_game(seeded_game_state_three)
    assert winning_players == [player_two]
    assert cheating_players == []


def test_run_game_cheaters(referee, game_state_with_forever_player, player_forever, player_three):
    winning_players, cheating_players = referee.run_game(game_state_with_forever_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_forever]


# TODO: figure out why there's more than one cheater
def test_run_game_multiple_cheaters(referee, game_state_with_forever_player_two, player_forever, player_three):
    winning_players, cheating_players = referee.run_game(game_state_with_forever_player_two)
    assert winning_players == [player_three]
    assert cheating_players == [player_forever]
