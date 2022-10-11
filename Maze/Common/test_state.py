import pytest
from board import Board
from state import State
from tile import Tile
from shapes import Line
from gem import Gem
from direction import Direction


@pytest.fixture
def seeded_board():
    return Board(seed=10)


@pytest.fixture
def seeded_spare_tile():
    return Tile(Line(0), Gem('emerald'), Gem('rhodonite'))

@pytest.fixture
def rotated_seeded_spare_tile():
    return Tile(Line(1), Gem('emerald'), Gem('rhodonite'))


@pytest.fixture
def sample_seeded_game_state(seeded_board):
    return State(seeded_board)


# ----- Test Rotate Method -----
# test rotate method works with a seeded board
def test_rotate(sample_seeded_game_state, seeded_spare_tile, rotated_seeded_spare_tile):
    board = sample_seeded_game_state.get_board()
    spare_tile = board.get_next_tile()
    assert spare_tile == seeded_spare_tile
    sample_seeded_game_state.rotate_spare_tile(90)
    rotated_spare_tile = board.get_next_tile()
    assert rotated_spare_tile == rotated_seeded_spare_tile


def test_rotate_twice(sample_seeded_game_state, seeded_spare_tile):
    board = sample_seeded_game_state.get_board()
    spare_tile = board.get_next_tile()
    assert spare_tile == seeded_spare_tile
    sample_seeded_game_state.rotate_spare_tile(-180)
    rotated_spare_tile = board.get_next_tile()
    assert rotated_spare_tile == seeded_spare_tile


# test rotate method throws exceptions when given invalid input
def test_rotate_invalid_input(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.rotate_spare_tile(89)
    assert str(error_message.value) == 'Invalid degrees of rotations. Must be multiple of 90 degrees.'


def test_rotate_invalid_input_negative(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.rotate_spare_tile(-1)
    assert str(error_message.value) == 'Invalid degrees of rotations. Must be multiple of 90 degrees.'

