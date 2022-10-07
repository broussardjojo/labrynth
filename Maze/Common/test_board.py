import pytest
from board import Board
from direction import Direction


# ------ Example Boards ------
@pytest.fixture
def basic_board():
    return Board()


# Test for the Board Constructor
def test_board_constructor():
    Board()


def test_board_constructor2():
    Board(15)


def test_board_constructor3():
    Board(7)


# ------------------------Test slide method---------------------------
# verify slide raises an exception when given an impossible move
def test_slide_out_of_bounds1(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide(-1, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds2(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide(7, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds3(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide(1, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


# verifies slide method modifies the removed tile
def test_removed_tile_initial_state(basic_board):
    assert basic_board.get_removed_tile() is None


def test_removed_tile_after_slide_down(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide(0, Direction.Down)
    assert basic_board.get_removed_tile() == tile_to_be_removed


def test_removed_tile_after_slide_right(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[2][6]
    basic_board.slide(2, Direction.Right)
    assert basic_board.get_removed_tile() == tile_to_be_removed


def test_removed_tile_after_slide_up(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[0][4]
    basic_board.slide(4, Direction.Up)
    assert basic_board.get_removed_tile() == tile_to_be_removed


def test_removed_tile_after_slide_left(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide(6, Direction.Left)
    assert basic_board.get_removed_tile() == tile_to_be_removed


# verifies that the slide method leaves an empty space for the next Tile in the correct spot
def test_slide_generates_gap_down(basic_board):
    basic_board.slide(2, Direction.Down)
    assert basic_board.get_tile_grid()[0][2] is None


def test_slide_generates_gap_right(basic_board):
    basic_board.slide(4, Direction.Right)
    assert basic_board.get_tile_grid()[4][0] is None


def test_slide_generates_gap_up(basic_board):
    basic_board.slide(0, Direction.Up)
    assert basic_board.get_tile_grid()[6][0] is None


def test_slide_generates_gap_left(basic_board):
    basic_board.slide(6, Direction.Left)
    assert basic_board.get_tile_grid()[6][6] is None


# ------------------------Test insert method---------------------------
# verifies the next tile gets inserted into the gap after calling insert
def test_insert_up(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide(0, Direction.Up)
    basic_board.insert_tile()
    assert next_tile == basic_board.get_tile_grid()[6][0]


def test_insert_right(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide(4, Direction.Right)
    basic_board.insert_tile()
    assert next_tile == basic_board.get_tile_grid()[4][0]


def test_insert_left(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide(2, Direction.Left)
    basic_board.insert_tile()
    assert next_tile == basic_board.get_tile_grid()[2][6]


def test_insert_down(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide(6, Direction.Down)
    basic_board.insert_tile()
    assert next_tile == basic_board.get_tile_grid()[0][6]


# verifies the next tile gets replaced by removed tile after insertion
def test_insert_replace_next1(basic_board):
    basic_board.slide(6, Direction.Down)
    removed_tile = basic_board.get_removed_tile()
    basic_board.insert_tile()
    assert removed_tile == basic_board.get_next_tile()


def test_insert_replace_next2(basic_board):
    basic_board.slide(4, Direction.Up)
    removed_tile = basic_board.get_removed_tile()
    basic_board.insert_tile()
    assert removed_tile == basic_board.get_next_tile()


# verifies insert raises exception if there are no gaps to insert into
def test_insert_no_gap(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.insert_tile()
    assert str(error_message.value) == 'No empty slots'
