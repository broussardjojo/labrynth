import pytest
from board import Board
from direction import Direction


# ------ Example Boards ------
@pytest.fixture
def basic_board():
    return Board.from_random_board()


@pytest.fixture
def seeded_small_board():
    return Board.from_random_board(3, seed=10)


# Test for the Board Constructor
def test_board_constructor():
    Board.from_random_board()


def test_board_constructor2():
    Board.from_random_board(15)


def test_board_constructor3():
    Board.from_random_board(7)


# ------------------------Test slide_and_insert method---------------------------
# verify slide raises an exception when given an impossible move
def test_slide_out_of_bounds1(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide_and_insert(-1, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds2(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide_and_insert(7, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds3(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide_and_insert(1, Direction.Up)
    assert str(error_message.value) == 'Invalid index'


# verifies slide method modifies the next tile
def test_removed_tile_after_slide_down(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide_and_insert(0, Direction.Down)
    assert basic_board.get_next_tile() == tile_to_be_removed


def test_removed_tile_after_slide_right(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[2][6]
    basic_board.slide_and_insert(2, Direction.Right)
    assert basic_board.get_next_tile() == tile_to_be_removed


def test_removed_tile_after_slide_up(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[0][4]
    basic_board.slide_and_insert(4, Direction.Up)
    assert basic_board.get_next_tile() == tile_to_be_removed


def test_removed_tile_after_slide_left(basic_board):
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide_and_insert(6, Direction.Left)
    assert basic_board.get_next_tile() == tile_to_be_removed


# verifies that the slide_and_insert method fills in the empty space in the correct spot with the next Tile
def test_slide_generates_gap_down(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(2, Direction.Down)
    assert basic_board.get_tile_grid()[0][2] is next_tile


def test_slide_generates_gap_right(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(4, Direction.Right)
    assert basic_board.get_tile_grid()[4][0] is next_tile


def test_slide_generates_gap_up(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(0, Direction.Up)
    assert basic_board.get_tile_grid()[6][0] is next_tile


def test_slide_generates_gap_left(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(6, Direction.Left)
    assert basic_board.get_tile_grid()[6][6] is next_tile


# ----- Test reachable_tiles method ------
def test_reachable_tiles_seeded_board(seeded_small_board):
    base_tile = seeded_small_board.get_tile_grid()[1][1]
    up_neighbor = seeded_small_board.get_tile_grid()[0][1]
    reachable_tiles = seeded_small_board.reachable_tiles(base_tile)
    assert up_neighbor in reachable_tiles


def test_reachable_tiles_not_reachable_seeded_board(seeded_small_board):
    base_tile = seeded_small_board.get_tile_grid()[1][1]
    right_neighbor = seeded_small_board.get_tile_grid()[1][2]
    reachable_tiles = seeded_small_board.reachable_tiles(base_tile)
    assert right_neighbor not in reachable_tiles


# ----- Test check_stationary_position method ------
# verifies that the given row and column are at a stationary position on the board
def test_check_stationary_position_one(basic_board):
    assert basic_board.check_stationary_position(1, 1)


def test_check_stationary_position_two(basic_board):
    assert basic_board.check_stationary_position(3, 5)


# verifies that the given row and column are not at a stationary position on the board
def test_check_stationary_position_three(basic_board):
    assert not basic_board.check_stationary_position(2, 0)


def test_check_stationary_position_four(basic_board):
    assert not basic_board.check_stationary_position(6, 3)


def test_check_stationary_position_five(basic_board):
    assert not basic_board.check_stationary_position(-1, -1)


def test_check_stationary_position_six(basic_board):
    assert not basic_board.check_stationary_position(9, 1)


# ----- Test get_all_stationary_tiles method ------
# verifies that the method returns the correct number of stationary tiles
def test_get_all_stationary_tiles_length(basic_board):
    assert len(basic_board.get_all_stationary_tiles()) == 9


def test_get_all_stationary_tiles_length_small_board(seeded_small_board):
    assert len(seeded_small_board.get_all_stationary_tiles()) == 1


# verifies that the method returns the correct stationary tiles
def test_get_all_stationary_tiles_one(basic_board):
    stationary_tile = basic_board.get_tile_grid()[1][1]
    assert stationary_tile in basic_board.get_all_stationary_tiles()


def test_get_all_stationary_tiles_two(basic_board):
    stationary_tile = basic_board.get_tile_grid()[3][5]
    assert stationary_tile in basic_board.get_all_stationary_tiles()


# verifies that the non-stationary tiles are not in the list of stationary tiles
def test_get_all_stationary_tiles_three(basic_board):
    stationary_tile = basic_board.get_tile_grid()[2][0]
    assert stationary_tile not in basic_board.get_all_stationary_tiles()


def test_get_all_stationary_tiles_four(basic_board):
    stationary_tile = basic_board.get_tile_grid()[1][4]
    assert stationary_tile not in basic_board.get_all_stationary_tiles()
