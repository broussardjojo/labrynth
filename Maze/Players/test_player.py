import pytest
from ..Common.state import ObservableState
from ..Common.board import Board
from .player import Player
from ..Common.position import Position
from .riemann import Riemann
from .euclid import Euclid


@pytest.fixture
def basic_board():
    return Board.from_random_board(7)


@pytest.fixture
def observable_state(basic_board):
    return ObservableState(basic_board)


@pytest.fixture
def basic_riemann():
    return Riemann()


@pytest.fixture
def basic_euclid():
    return Euclid()


@pytest.fixture
def basic_player(basic_riemann):
    return Player.from_goal_home_color_strategy(Position(1, 1), Position(3, 3), "purple", basic_riemann)


@pytest.fixture
def basic_player_two(basic_euclid):
    return Player.from_goal_home_color_strategy(Position(5, 5), Position(1, 3), "pink", basic_euclid)


# ------ Test the setup method which takes in two parameters (initialization) ------
def test_initial_setup(basic_player, observable_state):
    assert basic_player.get_goal_position() == Position(1, 1)
    basic_player.setup(observable_state, Position(1, 5))
    assert basic_player.get_goal_position() == Position(1, 5)


def test_initial_setup_two(basic_player, observable_state):
    assert basic_player.get_goal_position() == Position(1, 1)
    basic_player.setup(observable_state, Position(3, 1))
    assert basic_player.get_goal_position() == Position(3, 1)


def test_initial_setup_three(basic_player, observable_state):
    assert basic_player.get_goal_position() == Position(1, 1)
    basic_player.setup(observable_state, Position(1, 1))
    assert basic_player.get_goal_position() == Position(1, 1)


def test_initial_setup_player_two(basic_player_two, observable_state):
    assert basic_player_two.get_goal_position() == Position(5, 5)
    basic_player_two.setup(observable_state, Position(3, 5))
    assert basic_player_two.get_goal_position() == Position(3, 5)


def test_initial_setup_player_two_two(basic_player_two, observable_state):
    assert basic_player_two.get_goal_position() == Position(5, 5)
    basic_player_two.setup(observable_state, Position(1, 1))
    assert basic_player_two.get_goal_position() == Position(1, 1)


# ------ Test the setup method which takes in one parameter (reminder of home) ------
def test_setup_remind_home(basic_player):
    assert basic_player.get_goal_position() == Position(1, 1)
    basic_player.setup(basic_player.get_home_position())
    assert basic_player.get_goal_position() == Position(3, 3)


def test_setup_remind_home_given_arbitrary_position(basic_player):
    assert basic_player.get_goal_position() == Position(1, 1)
    basic_player.setup(Position(2, 4))
    assert basic_player.get_goal_position() == Position(2, 4)


def test_setup_player_two_remind_home(basic_player_two):
    assert basic_player_two.get_goal_position() == Position(5, 5)
    basic_player_two.setup(basic_player_two.get_home_position())
    assert basic_player_two.get_goal_position() == Position(1, 3)


def test_setup_player_two_remind_home_given_arbitrary_position(basic_player_two):
    assert basic_player_two.get_goal_position() == Position(5, 5)
    basic_player_two.setup(Position(6, 6))
    assert basic_player_two.get_goal_position() == Position(6, 6)


# --------- Test propose_board0 ------------
def test_propose_board_one(basic_player):
    assert len(basic_player.propose_board0(7, 7).get_tile_grid()) == 7


def test_propose_board_two(basic_player):
    assert len(basic_player.propose_board0(4, 9).get_tile_grid()) == 9


def test_propose_board_three(basic_player):
    seeded_board = Board.from_random_board(7, seed=7)
    assert basic_player.propose_board0(7, 7, seed=7) == seeded_board


def test_propose_board_four(basic_player):
    seeded_board = Board.from_random_board(7, seed=7)
    assert not basic_player.propose_board0(7, 7, seed=2) == seeded_board


def test_propose_board_even(basic_player):
    seeded_board = Board.from_random_board(6, seed=12)
    assert basic_player.propose_board0(5, 6, seed=12) == seeded_board



