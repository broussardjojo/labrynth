from pathlib import Path

import pytest
from ..Common.state import ObservableState
from ..Common.position import Position
from .riemann import Riemann
from .move import Move
from ..Common.direction import Direction
from ..Common.boardSerializer import get_json_obj_list, make_board
from ..Common.board import Board


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


# ----- Test generate_move method -----
# test generate_move method returns a valid Move to the goal when available
def test_generate_move_to_goal_one(riemann_strategy, observable_state, current_position, target_position):
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(0, Direction.Right, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_two(riemann_strategy, observable_state):
    current_position = Position(4, 4)
    target_position = Position(5, 5)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(4, Direction.Right, 0, target_position, False)
    assert move == desired_move


def test_generate_move_to_goal_using_spare_tile(riemann_strategy, observable_state):
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


# validates that the riemann strategy finds a non-goal tile when the goal tile is unreachable
def test_generate_move_cannot_reach_goal(riemann_strategy, observable_state):
    current_position = Position(2, 2)
    target_position = Position(3, 3)
    move = riemann_strategy.generate_move(observable_state, current_position, target_position)
    desired_move = Move(2, Direction.Left, 0, Position(0, 0), False)
    print(move)
    print(desired_move)
    assert move == desired_move
