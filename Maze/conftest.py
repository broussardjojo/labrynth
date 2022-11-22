import pytest

from Maze.Common.board import Board
from Maze.Common.utils import shape_dict


@pytest.fixture
def seeded_board():
    connector_rows = [
        "││┼└┼└│",
        "┬┬┼┬└└┼",
        "│└┬┬┼│┬",
        "└│┬│└┬│",
        "│└┼┬└┼└",
        "┼┬││└┼└",
        "└┬┼┼┬┼┼",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["│"])

@pytest.fixture
def seeded_board_3x9():
    connector_rows = [
        "││┼└┼└│└│",
        "┬┬┼┬└└┼└┼",
        "│└┬┬┼│┬│┬",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["│"])

@pytest.fixture
def seeded_board_9x3():
    connector_rows = [
        "││┼",
        "┬┬┼",
        "│└┬",
        "└│┬",
        "│└┼",
        "┼┬│",
        "└┬┼",
        "┼┬│",
        "└┬┼",
    ]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in connector_rows]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["│"])

@pytest.fixture
def seeded_board_dict(seeded_board, seeded_board_3x9, seeded_board_9x3):
    return {"7x7": seeded_board,
            "3x9": seeded_board_3x9,
            "9x3": seeded_board_9x3}