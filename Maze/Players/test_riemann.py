import pytest

from ..Common.board import Board
from ..Common.state import ObservableState
from .riemann import Riemann


@pytest.fixture
def sample_game_state(sample_board):
    return ObservableState(sample_board)


@pytest.fixture
def sample_riemann():
    return Riemann()


@pytest.fixture
def sample_board():
    return Board.from_random_board(7, seed=11)


def test_temp(sample_game_state, sample_riemann):
    beginning_tile = sample_game_state.get_board().get_tile_grid()[3][0]
    sample_riemann.possible_to_reach_tile_after_slide(sample_game_state)
    assert beginning_tile == sample_game_state.get_board().get_tile_grid()[3][0]