from pathlib import Path

import pytest
from ..Common.state import ObservableState
from ..Common.position import Position
from .riemann import Riemann
from .move import Move
from ..Common.direction import Direction
from ..Common.boardSerializer import get_json_obj_list, make_board
from ..Common.board import Board


# ----- Examples ------
# This board has the following shape:
#   ["┬","┐","─","─","┐","└","┌"],
#   ["└","│","─","┘","┬","├","┴"],
#   ["─","│","│","┐","│","│","─"],
#   ["┐","│","─","┬","┬","├","┴"],
#   ["┤","┼","│","┐","┐","└","│"],
#   ["┘","├","│","┬","┤","┼","│"],
#   ["─","┴","└","┐","┘","┬","├"]
# It's spare tile is a "┬" shape
@pytest.fixture
def basic_seeded_board():
    path = Path(__file__).parent / "basicBoard.json"
    with path.open() as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board.from_list_of_tiles(make_board(json_obj_list[0]), seed=30)


@pytest.fixture
def observable_state(basic_seeded_board):
    return ObservableState(basic_seeded_board)


@pytest.fixture
def current_position():
    return Position(0, 4)


@pytest.fixture
def target_position():
    return Position(3, 5)


@pytest.fixture
def riemann_strategy(target_position):
    return Riemann(target_position)


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
    with path.open() as board_file:
        board_data = board_file.read()
        json_obj_list = get_json_obj_list(board_data)
        return Board.from_list_of_tiles(make_board(json_obj_list[0]), seed=30)


@pytest.fixture
def observable_state_two(basic_seeded_board_two):
    return ObservableState(basic_seeded_board_two)


# ----- Test generate_move method -----
# test generate_move method returns a valid Move to the goal when available
def test_generate_move_to_goal_right_one(riemann_strategy, observable_state, current_position, target_position):
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(0, Direction.Right, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_right_two(riemann_strategy, observable_state):
    current_position = Position(4, 4)
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(4, Direction.Right, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_left(riemann_strategy, observable_state):
    current_position = Position(4, 6)
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(4, Direction.Left, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_up(riemann_strategy, observable_state):
    current_position = Position(2, 6)
    target_position = Position(1, 5)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(6, Direction.Up, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_down(riemann_strategy, observable_state):
    current_position = Position(1, 2)
    target_position = Position(2, 3)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(2, Direction.Down, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_using_spare_tile_no_rotation(riemann_strategy, observable_state):
    current_position = Position(2, 6)
    target_position = Position(3, 5)
    spare_tile = observable_state.get_board().get_next_tile()
    # Spare tile is a TShape in this shape: T
    assert spare_tile.has_path(Direction.Left)
    assert spare_tile.has_path(Direction.Down)
    assert not spare_tile.has_path(Direction.Up)
    assert spare_tile.has_path(Direction.Right)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(2, Direction.Left, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_using_spare_tile_with_rotation(riemann_strategy, observable_state):
    current_position = Position(3, 0)
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(4, Direction.Right, 90, target_position, False)
    assert move == desired_move


# validates that the riemann strategy finds a non-goal tile when the goal tile is unreachable
def test_generate_move_cannot_reach_goal_one(riemann_strategy, observable_state):
    current_position = Position(2, 2)
    target_position = Position(3, 3)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(2, Direction.Left, 0, Position(0, 0), False)
    assert move == desired_move


def test_generate_move_cannot_reach_goal_two(riemann_strategy, observable_state):
    current_position = Position(1, 3)
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(0, Direction.Left, 0, Position(0, 1), False)
    assert move == desired_move


def test_generate_move_cannot_reach_goal_three(riemann_strategy, observable_state):
    current_position = Position(5, 6)
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(6, Direction.Up, 0, Position(3, 6), False)
    assert move == desired_move


# validates the move is passed when no tile can be reached
def test_generate_passed_move_one(riemann_strategy, observable_state_two):
    current_position = Position(5, 5)
    target_position = Position(1, 1)
    move = riemann_strategy.generate_move(observable_state_two, current_position, target_position)
    desired_move = Move(3, Direction.Up, 0, Position(3, 6), True)
    assert move == desired_move


def test_generate_passed_move_two(riemann_strategy, observable_state_two):
    current_position = Position(4, 1)
    target_position = Position(5, 3)
    move = riemann_strategy.generate_move(observable_state_two, current_position, target_position)
    desired_move = Move(3, Direction.Up, 0, Position(3, 6), True)
    assert move == desired_move


# ------- Test possible_next_target_positions -------------
# verifies there are positions left when checked_positions is not full
def test_possible_next_target_positions_empty_list(riemann_strategy, observable_state):
    assert riemann_strategy.possible_next_target_positions(observable_state.get_board())


def test_possible_next_target_positions_partially_filled_list(riemann_strategy, observable_state):
    riemann_strategy.get_checked_positions().append(Position(-1, 0))
    riemann_strategy.get_checked_positions().append(Position(1, 7))
    riemann_strategy.get_checked_positions().append(Position(0, 0))
    assert riemann_strategy.possible_next_target_positions(observable_state.get_board())


def test_possible_next_target_positions_filled_list(riemann_strategy, observable_state):
    for row in range(7):
        for col in range(7):
            riemann_strategy.get_checked_positions().append(Position(row, col))
    assert not riemann_strategy.possible_next_target_positions(observable_state.get_board())


# ------- Test get_next_target_position -------------
# verifies the goal_position is returned when the list of checked positions is empty
def test_get_next_target_position(riemann_strategy, observable_state, target_position):
    assert len(riemann_strategy.get_checked_positions()) == 0
    assert riemann_strategy.get_next_target_position(observable_state.get_board()) == target_position


# verifies the first non-target-position is (0,0)
def test_get_next_target_position_target_not_available(riemann_strategy, observable_state, target_position):
    riemann_strategy.get_checked_positions().append(target_position)
    assert riemann_strategy.get_next_target_position(observable_state.get_board()) == Position(0, 0)


# verifies the second non-target-position is (0,1)
def test_get_next_target_position_target_or_top_left_not_available(riemann_strategy, observable_state, target_position):
    riemann_strategy.get_checked_positions().append(target_position)
    riemann_strategy.get_checked_positions().append(Position(0, 0))
    assert riemann_strategy.get_next_target_position(observable_state.get_board()) == Position(0, 1)


# verifies the riemann strategy goes row by row
def test_get_next_target_position_next_row(riemann_strategy, observable_state, target_position):
    riemann_strategy.get_checked_positions().append(target_position)
    for col in range(7):
        riemann_strategy.get_checked_positions().append(Position(0, col))
    assert riemann_strategy.get_next_target_position(observable_state.get_board()) == Position(1, 0)


# verifies the last target to check is position (6,6)
def test_get_next_target_position_last_position(riemann_strategy, observable_state, target_position):
    for row in range(7):
        for col in range(7):
            riemann_strategy.get_checked_positions().append(Position(row, col))
    riemann_strategy.get_checked_positions().remove(Position(6, 6))
    assert riemann_strategy.get_next_target_position(observable_state.get_board()) == Position(6, 6)


# verifies a value error is raised when there are no more targets to check
def test_get_next_target_position_no_positions(riemann_strategy, observable_state, target_position):
    with pytest.raises(ValueError) as error_message:
        for row in range(7):
            for col in range(7):
                riemann_strategy.get_checked_positions().append(Position(row, col))
        riemann_strategy.get_next_target_position(observable_state.get_board())
    assert str(error_message.value) == "Error: No Positions left to check"
