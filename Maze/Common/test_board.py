import itertools
import random
from copy import deepcopy
from typing import Iterable, List, TypeVar

import pytest
from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.gem import Gem
from Maze.Common.position import Position
from Maze.Common.tile import Tile
from Maze.Common.shapes import Corner, Cross
from Maze.Common.utils import get_connector_from_shape, shape_dict

T = TypeVar("T")


def board_to_unicode(board):
    result = ""
    for row, tiles in enumerate(board.get_tile_grid()):
        if result:
            result += "\n"
        result += "".join([get_connector_from_shape(tile.get_shape()) for tile in tiles])
        # if row == 0:
        #     result += " "
        #     result += get_connector_from_shape(board.get_next_tile().get_shape())
    return result


def flatten(nested: Iterable[Iterable[T]]) -> List[T]:
    return list(itertools.chain.from_iterable(nested))


# ------ Example Boards ------
@pytest.fixture
def basic_board():
    return Board.from_random_board()


@pytest.fixture
def small_board():
    board_connectors = [
        "┤┤┤",
        "├┤┤",
        "┤┤┤",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in board_connectors]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["┤"])


@pytest.fixture
def seeded_small_board():
    return Board.from_random_board(3, 3, rand=random.Random(10))


@pytest.fixture
def seeded_wide_board():
    return Board.from_random_board(3, 10, rand=random.Random(10))


@pytest.fixture
def seeded_narrow_board():
    return Board.from_random_board(10, 3, rand=random.Random(10))


@pytest.fixture
def snake_board_6x7():
    connector_rows = [
        '┌─────┘',
        '└─────┐',
        '┌─────┘',
        '└─────┐',
        '┌─────┘',
        '└─────┐',
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["│"])


@pytest.fixture
def concentric_board_6x6():
    connector_rows = [
        '┌────┐',
        '│┌──┐│',
        '││┌┐││',
        '││└┘││',
        '│└──┘│',
        '└────┘',
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["│"])


@pytest.fixture
def basic_corner():
    return Corner(0)


@pytest.fixture
def corner_tile(basic_corner):
    return Tile(basic_corner, Gem('amethyst'), Gem('amethyst'))


@pytest.fixture
def basic_cross():
    return Cross()


@pytest.fixture
def cross_tile(basic_cross):
    return Tile(basic_cross, Gem('emerald'), Gem('ammolite'))


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
        basic_board.slide_and_insert(-1, Direction.UP)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds2(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide_and_insert(7, Direction.UP)
    assert str(error_message.value) == 'Invalid index'


def test_slide_out_of_bounds3(basic_board):
    with pytest.raises(ValueError) as error_message:
        basic_board.slide_and_insert(1, Direction.UP)
    assert str(error_message.value) == 'Invalid index'


# verifies slide method modifies the next tile
def test_removed_tile_after_slide_down(basic_board):
    tile_grid_copy = deepcopy(basic_board.get_tile_grid())
    spare_tile = deepcopy(basic_board.get_next_tile())
    tile_to_be_removed = basic_board.get_tile_grid()[6][0]
    basic_board.slide_and_insert(0, Direction.DOWN)
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
    basic_board.slide_and_insert(2, Direction.RIGHT)
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
    basic_board.slide_and_insert(4, Direction.UP)
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
    basic_board.slide_and_insert(6, Direction.LEFT)
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
    basic_board.slide_and_insert(2, Direction.DOWN)
    assert basic_board.get_tile_grid()[0][2] is next_tile


def test_slide_generates_gap_right(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(4, Direction.RIGHT)
    assert basic_board.get_tile_grid()[4][0] is next_tile


def test_slide_generates_gap_up(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(0, Direction.UP)
    assert basic_board.get_tile_grid()[6][0] is next_tile


def test_slide_generates_gap_left(basic_board):
    next_tile = basic_board.get_next_tile()
    basic_board.slide_and_insert(6, Direction.LEFT)
    assert basic_board.get_tile_grid()[6][6] is next_tile


# ----- Test reachable_tiles method ------
def test_reachable_tiles_small_board(small_board):
    reachable_tiles = small_board.reachable_tiles(Position(1, 1))
    assert Position(0, 1) in reachable_tiles


def test_reachable_tiles_not_reachable_small_board(small_board):
    reachable_tiles = small_board.reachable_tiles(Position(1, 1))
    assert Position(1, 2) not in reachable_tiles


all_positions_6x7 = [Position(row, col) for row, col in itertools.product(range(6), range(7))]


@pytest.mark.parametrize("start_pos", all_positions_6x7)
def test_reachable_tiles_snake_board(snake_board_6x7, start_pos):
    assert snake_board_6x7.reachable_tiles(start_pos) == set(all_positions_6x7)


outer_ring_6x6 = [
    Position(row, col)
    for row, col in itertools.chain(itertools.product([0], range(6)),  # top
                                    itertools.product(range(6), [5]),  # right
                                    itertools.product([5], range(6)),  # bottom
                                    itertools.product(range(6), [0]))  # left
]
middle_ring_6x6 = [
    Position(1, 1), Position(1, 2), Position(1, 3), Position(1, 4),  # top
    Position(2, 4), Position(3, 4),                                  # right
    Position(4, 4), Position(4, 3), Position(4, 2), Position(4, 1),  # bottom
    Position(3, 1), Position(2, 1),                                  # left
]
inner_ring_6x6 = [
    Position(2, 2), Position(2, 3), Position(3, 3), Position(3, 2)
]


@pytest.mark.parametrize("start_pos, expected", flatten(
    [(start_pos, set(ring)) for start_pos in ring]
    for ring in [outer_ring_6x6, middle_ring_6x6, inner_ring_6x6]
))
def test_reachable_tiles_concentric_board(concentric_board_6x6, start_pos, expected):
    # outer ring, middle ring, inner ring are the 3 connected components
    assert concentric_board_6x6.reachable_tiles(start_pos) == expected


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


# ----- Test can_slide_horizontal method ------
@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2, 4, 6)],
    *[(col, False) for col in (1, 3, 5)],
    *[(col, False) for col in (-2, -1, 7, 8)]
])
def test_can_slide_horizontal_on_board(basic_board, slide_index, expected):
    assert basic_board.can_slide_horizontally(slide_index) == expected


@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2)],
    *[(col, False) for col in (1,)],
    *[(col, False) for col in (-2, -1, 3, 4)],
])
def test_can_slide_horizontal_on_wide_board(seeded_wide_board, slide_index, expected):
    assert seeded_wide_board.can_slide_horizontally(slide_index) == expected


@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2, 4, 6, 8)],
    *[(col, False) for col in (1, 3, 5, 7, 9)],
    *[(col, False) for col in (-2, -1, 10, 11)],
])
def test_can_slide_horizontal_on_narrow_board(seeded_narrow_board, slide_index, expected):
    assert seeded_narrow_board.can_slide_horizontally(slide_index) == expected


# ----- Test can_slide_vertically method ------
@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2, 4, 6)],
    *[(col, False) for col in (1, 3, 5)],
    *[(col, False) for col in (-2, -1, 7, 8)]
])
def test_can_slide_on_board(basic_board, slide_index, expected):
    assert basic_board.can_slide_vertically(slide_index) == expected


@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2, 4, 6, 8)],
    *[(col, False) for col in (1, 3, 5, 7, 9)],
    *[(col, False) for col in (-2, -1, 10, 11)],
])
def test_can_slide_on_wide_board(seeded_wide_board, slide_index, expected):
    assert seeded_wide_board.can_slide_vertically(slide_index) == expected


@pytest.mark.parametrize("slide_index, expected", [
    *[(col, True) for col in (0, 2)],
    *[(col, False) for col in (1,)],
    *[(col, False) for col in (-2, -1, 3, 4)],
])
def test_can_slide_on_narrow_board(seeded_narrow_board, slide_index, expected):
    assert seeded_narrow_board.can_slide_vertically(slide_index) == expected
