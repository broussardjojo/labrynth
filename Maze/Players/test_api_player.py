# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name
import pytest

from .api_player import LocalPlayer
from ..Common.abstract_state import AbstractState
from ..Common.board import Board
from .riemann import Riemann
from .euclid import Euclid


@pytest.fixture
def basic_board():
    return Board.from_random_board(7)


@pytest.fixture
def observable_state(basic_board):
    return AbstractState(basic_board, [])


@pytest.fixture
def basic_riemann():
    return Riemann()


@pytest.fixture
def basic_euclid():
    return Euclid()


@pytest.fixture
def basic_player(basic_riemann):
    return LocalPlayer("player1", basic_riemann)


@pytest.fixture
def basic_player_two(basic_euclid):
    return LocalPlayer("player2", basic_euclid)

# --------- Test propose_board0 ------------
def test_propose_board_one(basic_player):
    assert len(basic_player.propose_board0(7, 7).get_tile_grid()) == 7


def test_propose_board_two(basic_player):
    assert len(basic_player.propose_board0(4, 9).get_tile_grid()) == 9


# def test_propose_board_three(basic_player):
#     seeded_board = Board.from_random_board(7, seed=7)
#     assert basic_player.propose_board0(7, 7, seed=7) == seeded_board
#
#
# def test_propose_board_four(basic_player):
#     seeded_board = Board.from_random_board(7, seed=7)
#     assert not basic_player.propose_board0(7, 7, seed=2) == seeded_board
#
#
# def test_propose_board_even(basic_player):
#     seeded_board = Board.from_random_board(6, seed=12)
#     assert basic_player.propose_board0(5, 6, seed=12) == seeded_board

