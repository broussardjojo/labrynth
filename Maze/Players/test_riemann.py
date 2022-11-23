# pylint: disable=missing-class-docstring,missing-function-docstring,redefined-outer-name
from pathlib import Path

import pytest

from Maze.Players.move import Move, Pass
from Maze.Players.riemann import Riemann
from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.player_details import PlayerDetails
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Common.utils import get_json_obj_list, shape_dict
from Maze.JSON.deserializers import get_tile_grid_from_json


# ----- Examples ------
# This board has the following shape:
#   ["┬","┐","─","─","┐","└","┌"],
#   ["└","│","─","┘","┬","├","┴"],
#   ["─","│","│","┐","│","│","─"],
#   ["┐","│","─","┬","┬","├","┴"],
#   ["┤","┼","│","┐","┐","└","│"],
#   ["┘","├","│","┬","┤","┼","│"],
#   ["─","┴","└","┐","┘","┬","├"]
# It's spare tile is a "┤" shape
@pytest.fixture
def basic_seeded_board():
    board_connectors = [["┬", "┐", "─", "─", "┐", "└", "┌"],
    ["└", "│", "─", "┘", "┬", "├", "┴"],
    ["─", "│", "│", "┐", "│", "│", "─"],
    ["┐", "│", "─", "┬", "┬", "├", "┴"],
    ["┤", "┼", "│", "┐", "┐", "└", "│"],
    ["┘", "├", "│", "┬", "┤", "┼", "│"],
    ["─", "┴", "└", "┐", "┘", "┬", "├"]]
    shape_grid = [[shape_dict[connector] for connector in cr] for cr in board_connectors]
    return Board.from_list_of_shapes(shape_grid, next_tile_shape=shape_dict["┤"])


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
    path = Path(__file__).parent / "basicBoardTwo.json"
    with path.open(encoding="utf-8") as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board.from_list_of_tiles(get_tile_grid_from_json(json_obj_list[0]), seed=30)


@pytest.fixture
def observable_state(basic_seeded_board, current_position):
    return RedactedState(basic_seeded_board, [], [PlayerDetails(current_position, current_position, "red")], 0)


@pytest.fixture
def observable_state_two(basic_seeded_board_two, current_position):
    return RedactedState(basic_seeded_board_two, [], [PlayerDetails(current_position, current_position, "blue")], 0)


@pytest.fixture
def current_position():
    return Position(0, 4)


@pytest.fixture
def target_position():
    return Position(3, 5)


@pytest.fixture
def riemann_strategy():
    return Riemann()


# ----- Test generate_move method -----
# test generate_move method returns a valid Move to the goal when available
def test_generate_move_to_goal_right_one(riemann_strategy, observable_state, target_position):
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(0, Direction.RIGHT, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_right_two(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(4, 4))
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(4, Direction.RIGHT, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_left(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(4, 6))
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(4, Direction.LEFT, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_up(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(2, 6))
    target_position = Position(1, 5)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(6, Direction.UP, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_down(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(1, 2))
    target_position = Position(2, 3)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(2, Direction.DOWN, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_using_spare_tile_no_rotation(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(2, 6))
    target_position = Position(3, 5)
    spare_tile = observable_state.get_board().get_next_tile()
    # Spare tile is a TShape in this shape: T
    assert spare_tile.has_path(Direction.LEFT)
    assert spare_tile.has_path(Direction.DOWN)
    assert spare_tile.has_path(Direction.UP)
    assert not spare_tile.has_path(Direction.RIGHT)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(2, Direction.LEFT, 0, target_position)
    assert move == desired_move


def test_generate_move_to_goal_using_spare_tile_with_rotation(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(3, 0))
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(4, Direction.RIGHT, 180, target_position)
    assert move == desired_move


# validates that the riemann strategy finds a non-goal tile when the goal tile is unreachable
def test_generate_move_cannot_reach_goal_one(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(2, 2))
    target_position = Position(3, 3)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(2, Direction.LEFT, 0, Position(0, 0))
    assert move == desired_move


def test_generate_move_cannot_reach_goal_two(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(1, 3))
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(0, Direction.LEFT, 0, Position(0, 1))
    assert move == desired_move


def test_generate_move_cannot_reach_goal_three(riemann_strategy, observable_state):
    observable_state.get_active_player().set_current_position(Position(5, 6))
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state, target_position)
    desired_move = Move(6, Direction.UP, 0, Position(3, 6))
    assert move == desired_move


# validates the move is passed when no tile can be reached
def test_generate_passed_move_one(riemann_strategy, observable_state_two):
    observable_state_two.get_active_player().set_current_position(Position(5, 5))
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state_two, target_position)
    desired_move = Pass()
    assert move == desired_move


def test_generate_passed_move_two(riemann_strategy, observable_state_two):
    observable_state_two.get_active_player().set_current_position(Position(4, 1))
    target_position = Position(5, 3)
    move = riemann_strategy.generate_move(observable_state_two, target_position)
    desired_move = Pass()
    assert move == desired_move
