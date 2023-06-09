# pylint: disable=missing-function-docstring,redefined-outer-name
import itertools

import pytest
from Maze.Common.board import Board
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.state import State
from Maze.Common.tile import Tile
from Maze.Common.shapes import Line
from Maze.Common.gem import Gem
from Maze.Common.direction import Direction
from Maze.Common.position import Position
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
def seeded_spare_tile():
    return Tile(Line(0), Gem('emerald'), Gem('emerald'))


@pytest.fixture
def rotated_seeded_spare_tile():
    return Tile(Line(1), Gem('emerald'), Gem('emerald'))


@pytest.fixture
def player_one():
    return RefereePlayerDetails.from_home_goal_color(Position(5, 1), Position(3, 1), "pink")


@pytest.fixture
def player_two():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 3), Position(5, 5), "red")


@pytest.fixture
def player_three():
    return RefereePlayerDetails.from_home_goal_color(Position(3, 1), Position(1, 1), "black")


@pytest.fixture
def sample_seeded_game_state(seeded_board, player_one, player_two, player_three):
    return State.from_board_and_players(seeded_board, [player_one, player_two, player_three])


@pytest.fixture
def concentric_6x6_game_state(concentric_board_6x6, player_one, player_two, player_three):
    return State.from_board_and_players(concentric_board_6x6, [player_one, player_two, player_three])


@pytest.fixture
def zero_player_game_state(seeded_board):
    return State.from_board_and_players(seeded_board, [])


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


# ----- Test kick_out_active_player Method -----
# verifies kick_out_active_player removes the currently active player from the State
def test_kick_out_active_player(sample_seeded_game_state):
    active_player = sample_seeded_game_state.get_players()[0]
    sample_seeded_game_state.kick_out_active_player()
    assert active_player not in sample_seeded_game_state.get_players()


def test_do_not_kick_out_non_active_player(sample_seeded_game_state):
    not_active_player = sample_seeded_game_state.get_players()[1]
    sample_seeded_game_state.kick_out_active_player()
    assert not_active_player in sample_seeded_game_state.get_players()


def test_kick_out_two_active_players_in_a_row(sample_seeded_game_state):
    second_active_player = sample_seeded_game_state.get_players()[1]
    sample_seeded_game_state.kick_out_active_player()
    sample_seeded_game_state.kick_out_active_player()
    assert second_active_player not in sample_seeded_game_state.get_players()


# verifies kick_out_active_player raises exception when there are no players to kick out
def test_kick_out_one_player_too_many(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
    assert str(error_message.value) == "No players to remove"


# ----- Test is_active_player_at_goal Method -----
# verifies the method returns true when the active player is at their goal Tile
def test_is_active_player_not_at_goal(sample_seeded_game_state):
    assert not sample_seeded_game_state.is_active_player_at_goal()


def test_is_active_player_at_goal(sample_seeded_game_state):
    active_player = sample_seeded_game_state.get_players()[0]
    goal_tile = active_player.get_goal_position()
    sample_seeded_game_state.move_active_player_to(goal_tile)
    assert sample_seeded_game_state.is_active_player_at_goal()


# verifies is_active_player_at_goal raises exception when there are no players
def test_is_active_player_at_goal_no_players(zero_player_game_state):
    with pytest.raises(ValueError) as error_message:
        zero_player_game_state.is_active_player_at_goal()
    assert str(error_message.value) == "No players to check"


def test_is_active_player_at_goal_removed_all_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.is_active_player_at_goal()
    assert str(error_message.value) == "No players to check"


# ----- Test get_legal_destinations Method -----

outer_ring_6x6 = [
    Position(row, col)
    for row, col in itertools.chain(itertools.product([0], range(6)),  # top
                                    itertools.product(range(6), [5]),  # right
                                    itertools.product([5], range(6)),  # bottom
                                    itertools.product(range(6), [0]))  # left
]
middle_ring_6x6 = [
    Position(1, 1), Position(1, 2), Position(1, 3), Position(1, 4),  # top
    Position(2, 4), Position(3, 4),  # right
    Position(4, 4), Position(4, 3), Position(4, 2), Position(4, 1),  # bottom
    Position(3, 1), Position(2, 1),  # left
]
inner_ring_6x6 = [
    Position(2, 2), Position(2, 3), Position(3, 3), Position(3, 2)
]


def test_reachable_destinations_player_one(concentric_6x6_game_state):
    assert concentric_6x6_game_state.get_legal_destinations() == set(outer_ring_6x6) - {Position(5, 1)}
    concentric_6x6_game_state.slide_and_insert(4, Direction.RIGHT)
    # '┌────┐',
    # '│┌──┐│',
    # '││┌┐││',
    # '││└┘││',
    # '││└──┘',
    # '└────┘',
    #   ^p1
    made_reachable = {Position(4, 2), Position(4, 3), Position(4, 4)}
    all_reachable = set(outer_ring_6x6) | made_reachable
    assert concentric_6x6_game_state.get_legal_destinations() == all_reachable - {Position(5, 1)}


def test_reachable_destinations_player_two(concentric_6x6_game_state):
    concentric_6x6_game_state.change_active_player_turn()
    assert concentric_6x6_game_state.get_legal_destinations() == set(inner_ring_6x6) - {Position(3, 3)}
    concentric_6x6_game_state.slide_and_insert(2, Direction.LEFT)
    # '┌────┐',
    # '│┌──┐│',
    # '│┌┐│││',
    # '││└┘││', <-p2@(3,3)
    # '│└──┘│',
    # '└────┘',
    #     ^
    all_reachable = set(inner_ring_6x6 + middle_ring_6x6)
    assert concentric_6x6_game_state.get_legal_destinations() == all_reachable - {Position(3, 3)}


# ----- Test slide Method -----
# Test that the slide method adjusts the players' positions if needed, testing the slide method itself
# is done on the board
def test_slide_does_not_move_stationary_players(sample_seeded_game_state):
    pre_slide_positions = {}
    for player in sample_seeded_game_state.get_players():
        pre_slide_positions[player] = (player.get_current_position())
    sample_seeded_game_state.slide_and_insert(0, Direction.DOWN)
    for player in sample_seeded_game_state.get_players():
        assert player.get_current_position() == pre_slide_positions[player]


def test_slide_bumps_player_on_edge(sample_seeded_game_state):
    player_one = sample_seeded_game_state.get_players()[0]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    edge_tile_pos = Position(6, 0)
    player_one.set_current_position(edge_tile_pos)
    assert player_one.get_current_position() == edge_tile_pos
    sample_seeded_game_state.slide_and_insert(0, Direction.DOWN)
    assert sample_seeded_game_state.get_board().get_tile_grid()[0][0] == next_tile
    assert player_one.get_current_position() == Position(0, 0)


def test_slide_bumps_two_players_on_edge(sample_seeded_game_state):
    player_one = sample_seeded_game_state.get_players()[0]
    player_two = sample_seeded_game_state.get_players()[1]
    player_three = sample_seeded_game_state.get_players()[2]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    edge_tile_pos = Position(2, 6)
    unbumped_tile_pos = Position(1, 5)
    player_one.set_current_position(edge_tile_pos)
    player_two.set_current_position(unbumped_tile_pos)
    player_three.set_current_position(edge_tile_pos)
    assert player_one.get_current_position() == edge_tile_pos
    assert player_two.get_current_position() == unbumped_tile_pos
    assert player_three.get_current_position() == edge_tile_pos
    sample_seeded_game_state.slide_and_insert(2, Direction.RIGHT)
    assert sample_seeded_game_state.get_board().get_tile_grid()[2][0] == next_tile
    assert player_one.get_current_position() == Position(2, 0)
    assert player_two.get_current_position() == unbumped_tile_pos
    assert player_three.get_current_position() == Position(2, 0)


# ----- Tests for change_active_player_turn ------
def test_change_active_player_turn_not_at_end(sample_seeded_game_state):
    assert sample_seeded_game_state.get_active_player_index() == 0
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 1


def test_change_active_player_turn_at_end(sample_seeded_game_state):
    assert sample_seeded_game_state.get_active_player_index() == 0
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 1
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 2
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 0


# ----- Test is_active_player_at_goal Method -----
# verifies the method returns true when the active player is at their home Position
def test_is_active_player_at_home(sample_seeded_game_state):
    assert sample_seeded_game_state.is_active_player_at_home()


def test_is_active_player_not_at_home(sample_seeded_game_state):
    active_player = sample_seeded_game_state.get_players()[0]
    goal_position = active_player.get_goal_position()
    sample_seeded_game_state.move_active_player_to(goal_position)
    assert not sample_seeded_game_state.is_active_player_at_home()


# ----- Test the move_active_player_to method -----
# validates that the move active player moves the currently active player to the specified location
def test_move_active_player_to_moves_active(sample_seeded_game_state):
    active_player = sample_seeded_game_state.get_players()[0]
    assert active_player.get_current_position() == Position(5, 1)
    sample_seeded_game_state.move_active_player_to(Position(0, 4))
    assert active_player.get_current_position() == Position(0, 4)


def test_move_active_player_to_moves_active_two(sample_seeded_game_state):
    active_player = sample_seeded_game_state.get_players()[0]
    assert active_player.get_current_position() == Position(5, 1)
    sample_seeded_game_state.move_active_player_to(Position(6, 6))
    assert active_player.get_current_position() == Position(6, 6)


def test_move_active_player_to_does_not_move_inactive(sample_seeded_game_state):
    non_active_player_one = sample_seeded_game_state.get_players()[1]
    non_active_player_two = sample_seeded_game_state.get_players()[2]
    assert non_active_player_one.get_current_position() == Position(3, 3)
    assert non_active_player_two.get_current_position() == Position(3, 1)
    sample_seeded_game_state.move_active_player_to(Position(6, 6))
    assert non_active_player_one.get_current_position() == Position(3, 3)
    assert non_active_player_two.get_current_position() == Position(3, 1)


# ----- Test active_player_has_reached_goal ---------
def test_active_player_has_reached_goal(sample_seeded_game_state):
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    assert sample_seeded_game_state.update_active_player_goals_reached()
    assert sample_seeded_game_state.active_player_has_reached_goal()


def test_active_player_has_not_reached_goal_one(sample_seeded_game_state):
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    assert not sample_seeded_game_state.active_player_has_reached_goal()
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    assert sample_seeded_game_state.update_active_player_goals_reached()
    assert sample_seeded_game_state.active_player_has_reached_goal()


def test_active_player_has_not_reached_goal_two(sample_seeded_game_state):
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    sample_seeded_game_state.is_active_player_at_goal()
    sample_seeded_game_state.change_active_player_turn()
    assert not sample_seeded_game_state.active_player_has_reached_goal()


# ---- Test get_closest_player_to_victory ---------
def test_get_closest_player_to_victory_no_goals_start(sample_seeded_game_state, player_one, player_three):
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_one, player_three]


def test_get_closest_player_to_victory_no_goals_moved(sample_seeded_game_state, player_one,
                                                      player_two, player_three):
    player_one.set_current_position(Position(4, 6))
    player_two.set_current_position(Position(0, 0))
    player_three.set_current_position(Position(5, 3))
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_three]


def test_get_closest_player_to_victory_at_goal_moved(sample_seeded_game_state, player_one,
                                                     player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(2, 0))
    player_three.set_current_position(Position(3, 3))
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_one]


def test_get_closest_player_to_victory_at_goal_moved_two(sample_seeded_game_state, player_one,
                                                         player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(2, 0))
    player_three.set_current_position(Position(1, 1))
    assert sample_seeded_game_state.update_active_player_goals_reached()
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_one]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached(sample_seeded_game_state, player_one,
                                                                      player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(3, 3))
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_one.set_goal_position(player_one.get_home_position())
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_two.set_goal_position(player_two.get_home_position())
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_one]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached_two(sample_seeded_game_state,
                                                                          player_one,
                                                                          player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(2, 5))
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_one.set_goal_position(player_one.get_home_position())
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_two.set_goal_position(player_two.get_home_position())
    player_two.set_current_position(Position(3, 4))
    assert sample_seeded_game_state.get_closest_players_to_victory(True) == [player_two]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached_three(sample_seeded_game_state,
                                                                            player_one,
                                                                            player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(6, 0))
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_one.set_goal_position(player_one.get_home_position())
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.update_active_player_goals_reached()
    player_two.set_goal_position(player_two.get_home_position())
    player_two.set_current_position(Position(2, 3))
    player_one.set_current_position(Position(4, 1))
    assert player_one in sample_seeded_game_state.get_closest_players_to_victory(True)
    assert player_two in sample_seeded_game_state.get_closest_players_to_victory(True)
    assert player_three not in sample_seeded_game_state.get_closest_players_to_victory(True)


def test_get_closest_player_to_victory_no_players(zero_player_game_state):
    assert len(zero_player_game_state.get_players()) == 0
    assert zero_player_game_state.get_closest_players_to_victory(True) == []
