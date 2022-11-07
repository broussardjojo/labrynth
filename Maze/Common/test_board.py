from copy import deepcopy

import pytest
from .board import Board
from .direction import Direction
from .position import Position
from .tile import Tile
from .shapes import Corner, Cross


# ------ Example Boards ------
@pytest.fixture
def basic_board():
    return Board.from_random_board()


@pytest.fixture
def seeded_small_board():
    return Board.from_random_board(3, seed=10)


@pytest.fixture
def basic_corner():
    return Corner(0)


@pytest.fixture
def corner_tile(basic_corner):
    return Tile(basic_corner, 'amethyst', 'amethyst')


@pytest.fixture
def basic_cross():
    return Cross()


@pytest.fixture
def cross_tile(basic_cross):
    return Tile(basic_cross, 'emerald', 'ammolite')


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
    tile_grid_copy = deepcopy(basic_board.get_tile_grid())
    spare_tile = deepcopy(basic_board.get_next_tile())
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide_and_insert(0, Direction.Down)
    assert basic_board.get_next_tile() == tile_to_be_removed
    tile_grid_after = basic_board.get_tile_grid()
    for row, tiles in enumerate(tile_grid_copy):
        for col, tile in enumerate(tiles):
            if col == 0:
                if row < 6:
                    assert tile == tile_grid_after[row + 1][col]
            else:
                assert tile == tile_grid_after[row][col]
    assert tile_grid_after[0][0] == spare_tile


def test_removed_tile_after_slide_right(basic_board):
    tile_grid_copy = deepcopy(basic_board.get_tile_grid())
    spare_tile = deepcopy(basic_board.get_next_tile())
    tile_to_be_removed = basic_board.get_tile_grid()[2][6]
    basic_board.slide_and_insert(2, Direction.Right)
    assert basic_board.get_next_tile() == tile_to_be_removed
    tile_grid_after = basic_board.get_tile_grid()
    for row, tiles in enumerate(tile_grid_copy):
        for col, tile in enumerate(tiles):
            if row == 2:
                if col < 6:
                    assert tile == tile_grid_after[row][col + 1]
            else:
                assert tile == tile_grid_after[row][col]
    assert tile_grid_after[2][0] == spare_tile


def test_removed_tile_after_slide_up(basic_board):
    tile_grid_copy = deepcopy(basic_board.get_tile_grid())
    spare_tile = deepcopy(basic_board.get_next_tile())
    tile_to_be_removed = basic_board.get_tile_grid()[0][4]
    basic_board.slide_and_insert(4, Direction.Up)
    assert basic_board.get_next_tile() == tile_to_be_removed
    tile_grid_after = basic_board.get_tile_grid()
    for row, tiles in enumerate(tile_grid_copy):
        for col, tile in enumerate(tiles):
            if col == 4:
                if row > 0:
                    assert tile == tile_grid_after[row - 1][col]
            else:
                assert tile == tile_grid_after[row][col]
    assert tile_grid_after[6][4] == spare_tile


def test_removed_tile_after_slide_left(basic_board):
    tile_grid_copy = deepcopy(basic_board.get_tile_grid())
    spare_tile = deepcopy(basic_board.get_next_tile())
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide_and_insert(6, Direction.Left)
    assert basic_board.get_next_tile() == tile_to_be_removed
    tile_grid_after = basic_board.get_tile_grid()
    for row, tiles in enumerate(tile_grid_copy):
        for col, tile in enumerate(tiles):
            if row == 6:
                if col > 0:
                    assert tile == tile_grid_after[row][col - 1]
            else:
                assert tile == tile_grid_after[row][col]
    assert tile_grid_after[6][6] == spare_tile


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


# ----- Test get_position_by_tile method ------
# verifies that the method returns the correct position for a Tile
def test_valid_position_by_tile_one(basic_board):
    test_tile = basic_board.get_tile_grid()[5][3]
    target_position = Position(5, 3)
    assert basic_board.get_position_by_tile(test_tile) == target_position


def test_valid_position_by_tile_two(basic_board):
    test_tile = basic_board.get_tile_grid()[0][0]
    target_position = Position(0, 0)
    assert basic_board.get_position_by_tile(test_tile) == target_position


# verifies that the method raises a Value error for a Tile not on the Board
def test_invalid_position_by_tile_one(seeded_small_board, corner_tile):
    test_tile = corner_tile
    with pytest.raises(ValueError) as error_message:
        seeded_small_board.get_position_by_tile(test_tile)
    assert str(error_message.value) == "Tile not on board"


def test_invalid_position_by_tile_two(seeded_small_board, cross_tile):
    test_tile = cross_tile
    with pytest.raises(ValueError) as error_message:
        seeded_small_board.get_position_by_tile(test_tile)
    assert str(error_message.value) == "Tile not on board"


# ----- Test get_tile_by_position method ------
# verifies that the method returns the correct Tile for a Position
def test_valid_tile_by_position_one(seeded_small_board):
    test_tile = seeded_small_board.get_tile_grid()[0][1]
    test_position = Position(0, 1)
    assert seeded_small_board.get_tile_by_position(test_position) == test_tile


def test_valid_tile_by_position_two(seeded_small_board):
    test_tile = seeded_small_board.get_tile_grid()[2][2]
    test_position = Position(2, 2)
    assert seeded_small_board.get_tile_by_position(test_position) == test_tile


# verifies that the method raises a Value error for a Position not on the Board
def test_invalid_tile_by_position_too_big(basic_board):
    test_position = Position(7, 7)
    with pytest.raises(ValueError) as error_message:
        basic_board.get_tile_by_position(test_position)
    assert str(error_message.value) == "Position not on board"


def test_invalid_tile_by_position_negative(basic_board):
    test_position = Position(-1, 6)
    with pytest.raises(ValueError) as error_message:
        basic_board.get_tile_by_position(test_position)
    assert str(error_message.value) == "Position not on board"


# ----- Test can_slide method ------
def test_can_slide_on_board(basic_board):
    assert basic_board.can_slide(2)


def test_can_slide_on_board_two(basic_board):
    assert basic_board.can_slide(4)


def test_can_slide_not_on_board(basic_board):
    assert not basic_board.can_slide(-1)


def test_can_slide_not_on_board_two(basic_board):
    assert not basic_board.can_slide(7)


def test_can_slide_on_board_stationary(basic_board):
    assert not basic_board.can_slide(1)


def test_can_slide_on_board_stationary_two(basic_board):
    assert not basic_board.can_slide(3)
