import time
from pathlib import Path

import pytest

from ..Players.euclid import Euclid
from ..Players.move import Move
from ..Players.player import Player
from .referee import Referee
from ..Players.riemann import Riemann
from ..Players.strategy import Strategy
from ..Common.board import Board
from ..Common.boardSerializer import make_tile_grid
from ..Common.direction import Direction
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
    path = Path(__file__).parent.parent / "Players/basicBoard.json"
    with path.open(encoding="utf-8") as board_file:
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
    path = Path(__file__).parent.parent / "Players/basicBoardTwo.json"
    with path.open(encoding="utf-8") as board_file:
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
def player_five():
    return Player.from_goal_home_color_strategy(Position(1, 3), Position(3, 3), "yellow", Riemann())


@pytest.fixture
def referee_no_observer():
    return Referee()


@pytest.fixture
def referee_with_observer():
    return Referee(True)


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


class ForeverStrategy(Strategy):

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        while True:
            time.sleep(1)
        return Move(0, Direction.Up, 0, Position(2, 0))


@pytest.fixture
def forever_strategy():
    return ForeverStrategy()


@pytest.fixture
def player_forever(forever_strategy):
    return Player.from_goal_home_color_strategy(Position(1, 5), Position(3, 1), "green", forever_strategy)


@pytest.fixture
def game_state_with_forever_player(seeded_board, player_forever, player_two, player_three, player_four):
    return State.from_board_and_players(seeded_board, [player_forever, player_two, player_three, player_four])


@pytest.fixture
def game_state_with_forever_player_two(basic_seeded_board_two, player_forever, player_two, player_three, player_four):
    return State.from_board_and_players(basic_seeded_board_two, [player_forever, player_two, player_three, player_four])


class BadRotationStrategy(Strategy):

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        return Move(0, Direction.Up, 14, Position(2, 0))


@pytest.fixture
def bad_rotation_strategy():
    return BadRotationStrategy()


@pytest.fixture
def player_bad_rotation(bad_rotation_strategy):
    return Player.from_goal_home_color_strategy(Position(5, 3), Position(3, 5), "orange", bad_rotation_strategy)


@pytest.fixture
def game_state_with_bad_rotation_player(seeded_board, player_bad_rotation, player_three, player_four):
    return State.from_board_and_players(seeded_board, [player_bad_rotation, player_three, player_four])


class BadSlideIndexStrategy(Strategy):

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        return Move(1, Direction.Up, 90, Position(2, 0))


@pytest.fixture
def bad_slide_index_strategy():
    return BadSlideIndexStrategy()


@pytest.fixture
def player_bad_slide_index(bad_slide_index_strategy):
    return Player.from_goal_home_color_strategy(Position(5, 3), Position(3, 5), "yellow", bad_slide_index_strategy)


@pytest.fixture
def game_state_with_bad_slide_index_player(seeded_board, player_bad_slide_index, player_three, player_four):
    return State.from_board_and_players(seeded_board, [player_bad_slide_index, player_three, player_four])


class BadMoveToStrategy(Strategy):

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        return Move(0, Direction.Up, 90, Position(2, 0))


@pytest.fixture
def bad_move_to_strategy():
    return BadMoveToStrategy()


@pytest.fixture
def player_bad_move_to(bad_move_to_strategy):
    return Player.from_goal_home_color_strategy(Position(1, 3), Position(6, 5), "red", bad_move_to_strategy)


@pytest.fixture
def game_state_with_bad_move_to_player(seeded_board, player_bad_move_to, player_three, player_four):
    return State.from_board_and_players(seeded_board, [player_bad_move_to, player_three, player_four])

"""
# TODO: fix
# @pytest.fixture
# def game_state_all_cheaters(seeded_board, player_bad_move_to, player_forever, player_bad_slide_index,
#                             player_bad_rotation):
#     return State.from_board_and_players(seeded_board, [player_bad_move_to, player_forever, player_bad_slide_index,
#                                                        player_bad_rotation])

# ----- Test referee without observer ------

# ----- Test run_game -------
def test_run_game_results_one(referee_no_observer, seeded_game_state, player_one):
    winning_players, cheating_players = referee_no_observer.run_game(seeded_game_state)
    assert winning_players == [player_one]
    assert cheating_players == []


def test_run_game_results_two(referee_no_observer, seeded_game_state_two, player_three):
    winning_players, cheating_players = referee_no_observer.run_game(seeded_game_state_two)
    assert winning_players == [player_three]
    assert cheating_players == []


def test_run_game_all_pass(referee_no_observer, seeded_game_state_three, player_one, player_two, player_three):
    player_one.set_current_position(Position(5, 5))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    winning_players, cheating_players = referee_no_observer.run_game(seeded_game_state_three)
    assert winning_players == [player_two]
    assert cheating_players == []


# TODO: fix
# def test_run_game_one_cheater(referee_no_observer, game_state_with_forever_player, player_forever, player_three):
#     winning_players, cheating_players = referee_no_observer.run_game(game_state_with_forever_player)
#     assert winning_players == [player_three]
#     assert cheating_players == [player_forever]
#
#
# def test_run_game_one_cheater_two(referee_no_observer, game_state_with_forever_player_two, player_forever, player_three):
#     winning_players, cheating_players = referee_no_observer.run_game(game_state_with_forever_player_two)
#     assert winning_players == [player_three]
#     assert cheating_players == [player_forever]


def test_run_game_bad_rotation_cheater(referee_no_observer, game_state_with_bad_rotation_player, player_bad_rotation,
                                       player_three):
    winning_players, cheating_players = referee_no_observer.run_game(game_state_with_bad_rotation_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_rotation]


def test_run_game_bad_slide_index_cheater(referee_no_observer, game_state_with_bad_slide_index_player,
                                          player_bad_slide_index,
                                          player_three):
    winning_players, cheating_players = referee_no_observer.run_game(game_state_with_bad_slide_index_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_slide_index]


def test_run_game_bad_move_to_cheater(referee_no_observer, game_state_with_bad_move_to_player, player_bad_move_to,
                                      player_three):
    winning_players, cheating_players = referee_no_observer.run_game(game_state_with_bad_move_to_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_move_to]


# TODO: fix
# def test_run_game_all_cheaters(referee_no_observer, game_state_all_cheaters, player_bad_rotation, player_bad_slide_index,
#                                player_forever, player_bad_move_to):
#     winning_players, cheating_players = referee_no_observer.run_game(game_state_all_cheaters)
#     assert winning_players == []
#     assert cheating_players == [player_bad_move_to, player_forever, player_bad_slide_index,
#                                 player_bad_rotation]


def test_run_game_tie(referee_no_observer, seeded_game_state_four, player_one, player_three, player_five):
    player_one.set_current_position(Position(5, 5))
    player_five.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    winning_players, cheating_players = referee_no_observer.run_game(seeded_game_state_four)
    assert winning_players == [player_one, player_five]
    assert cheating_players == []


# ----- Test referee with observer ------

# ----- Test run_game -------
def test_run_game_results_1(referee_with_observer, seeded_game_state, player_one):
    winning_players, cheating_players = referee_with_observer.run_game(seeded_game_state)
    assert winning_players == [player_one]
    assert cheating_players == []


def test_run_game_results_2(referee_with_observer, seeded_game_state_two, player_three):
    winning_players, cheating_players = referee_with_observer.run_game(seeded_game_state_two)
    assert winning_players == [player_three]
    assert cheating_players == []


def test_run_game_all_pass_two(referee_with_observer, seeded_game_state_three, player_one, player_two, player_three):
    player_one.set_current_position(Position(5, 5))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    winning_players, cheating_players = referee_with_observer.run_game(seeded_game_state_three)
    assert winning_players == [player_two]
    assert cheating_players == []


# TODO: fix
# def test_run_game_one_cheater_1(referee_with_observer, game_state_with_forever_player, player_forever, player_three):
#     winning_players, cheating_players = referee_with_observer.run_game(game_state_with_forever_player)
#     assert winning_players == [player_three]
#     assert cheating_players == [player_forever]
#
#
# def test_run_game_one_cheater_2(referee_with_observer, game_state_with_forever_player_two, player_forever, player_three):
#     winning_players, cheating_players = referee_with_observer.run_game(game_state_with_forever_player_two)
#     assert winning_players == [player_three]
#     assert cheating_players == [player_forever]


def test_run_game_bad_rotation_cheater_two(referee_with_observer, game_state_with_bad_rotation_player,
                                           player_bad_rotation, player_three):
    winning_players, cheating_players = referee_with_observer.run_game(game_state_with_bad_rotation_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_rotation]


def test_run_game_bad_slide_index_cheater_two(referee_with_observer, game_state_with_bad_slide_index_player,
                                              player_bad_slide_index,
                                              player_three):
    winning_players, cheating_players = referee_with_observer.run_game(game_state_with_bad_slide_index_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_slide_index]


def test_run_game_bad_move_to_cheater_two(referee_with_observer, game_state_with_bad_move_to_player, player_bad_move_to,
                                          player_three):
    winning_players, cheating_players = referee_with_observer.run_game(game_state_with_bad_move_to_player)
    assert winning_players == [player_three]
    assert cheating_players == [player_bad_move_to]


# TODO: fix
# def test_run_game_all_cheaters_two(referee_with_observer, game_state_all_cheaters, player_bad_rotation, player_bad_slide_index,
#                                player_forever, player_bad_move_to):
#     winning_players, cheating_players = referee_with_observer.run_game(game_state_all_cheaters)
#     assert winning_players == []
#     assert cheating_players == [player_bad_move_to, player_forever, player_bad_slide_index,
#                                 player_bad_rotation]


def test_run_game_tie_two(referee_with_observer, seeded_game_state_four, player_one, player_three, player_five):
    player_one.set_current_position(Position(5, 5))
    player_five.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(5, 5))
    winning_players, cheating_players = referee_with_observer.run_game(seeded_game_state_four)
    assert winning_players == [player_one, player_five]
    assert cheating_players == []
"""