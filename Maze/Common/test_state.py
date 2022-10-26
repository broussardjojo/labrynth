import pytest
from .board import Board
from .state import State
from .tile import Tile
from .shapes import Line
from .gem import Gem
from .direction import Direction
from .position import Position
from ..Players.euclid import Euclid
from ..Players.player import Player
from ..Players.riemann import Riemann


@pytest.fixture
def seeded_board():
    return Board.from_random_board(seed=10)


@pytest.fixture
def seeded_spare_tile():
    return Tile(Line(0), Gem('emerald'), Gem('rhodonite'))


@pytest.fixture
def rotated_seeded_spare_tile():
    return Tile(Line(1), Gem('emerald'), Gem('rhodonite'))


@pytest.fixture
def sample_seeded_game_state(seeded_board):
    return State.from_random_state(seeded_board)


@pytest.fixture
def player_one():
    return Player.from_goal_home_color_strategy(Position(3, 1), Position(5, 1), "pink", Riemann())


@pytest.fixture
def player_two():
    return Player.from_goal_home_color_strategy(Position(5, 5), Position(3, 3), "red", Riemann())


@pytest.fixture
def player_three():
    return Player.from_goal_home_color_strategy(Position(1, 1), Position(3, 1), "black", Euclid())


@pytest.fixture
def sample_seeded_game_state_from_players(seeded_board, player_one, player_two, player_three):
    return State.from_board_and_players(seeded_board, [player_one, player_two, player_three])


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


# ----- Test add_player Method -----
# test add_player method adds a player to this State
def test_add_player_one(sample_seeded_game_state):
    assert sample_seeded_game_state.get_players() == []
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 1


def test_add_player_two(sample_seeded_game_state):
    assert sample_seeded_game_state.get_players() == []
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 1
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 2


def test_add_max_players(sample_seeded_game_state):
    assert sample_seeded_game_state.get_players() == []
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 1
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 2
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 3
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 4
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 5
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 6
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 7
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 8
    sample_seeded_game_state.add_player()
    assert len(sample_seeded_game_state.get_players()) == 9


# verifies add_player method does not allow adding of too many players
def test_add_player_too_many(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
    assert str(error_message.value) == "Game is full, no more players can be added"


# ----- Test kick_out_active_player Method -----
# verifies kick_out_active_player removes the currently active player from the State
def test_kick_out_active_player(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    active_player = sample_seeded_game_state.get_players()[0]
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.kick_out_active_player()
    assert active_player not in sample_seeded_game_state.get_players()


def test_do_not_kick_out_non_active_player(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    not_active_player = sample_seeded_game_state.get_players()[1]
    sample_seeded_game_state.kick_out_active_player()
    assert not_active_player in sample_seeded_game_state.get_players()


def test_kick_out_two_active_players_in_a_row(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    second_active_player = sample_seeded_game_state.get_players()[1]
    sample_seeded_game_state.kick_out_active_player()
    sample_seeded_game_state.kick_out_active_player()
    assert second_active_player not in sample_seeded_game_state.get_players()


# verifies kick_out_active_player raises exception when there are no players to kick out
def test_kick_out_one_player_too_many(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
    assert str(error_message.value) == "No players to remove"


def test_kick_out_one_player_from_no_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.kick_out_active_player()
    assert str(error_message.value) == "No players to remove"


# ----- Test is_active_player_at_goal Method -----
# verifies the method returns true when the active player is at their goal Tile
def test_is_active_player_not_at_goal(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    assert not sample_seeded_game_state.is_active_player_at_goal()


def test_is_active_player_at_goal(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    active_player = sample_seeded_game_state.get_players()[0]
    goal_tile = active_player.get_goal_position()
    sample_seeded_game_state.move_active_player_to(goal_tile)
    assert sample_seeded_game_state.is_active_player_at_goal()


# verifies is_active_player_at_goal raises exception when there are no players
def test_is_active_player_at_goal_no_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.is_active_player_at_goal()
    assert str(error_message.value) == "No players to check"


def test_is_active_player_at_goal_removed_all_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.is_active_player_at_goal()
    assert str(error_message.value) == "No players to check"


# ----- Test can_active_player_reach_given_tile Method -----
# verifies can_active_player_reach_given_tile returns True if the player can reach the given tile and False otherwise
def test_player_can_reach_tile_above(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile_pos = current_player.get_current_position()
    reachable_tile = current_board.get_tile_grid()[4][5]
    current_tile = sample_seeded_game_state.get_board().get_tile_by_position(current_tile_pos)
    # validate that reachable tile is reachable using previously tested reachable_tiles method
    assert reachable_tile in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert sample_seeded_game_state.can_active_player_reach_given_tile(reachable_tile)


def test_player_can_reach_tile_below(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile_pos = current_player.get_current_position()
    reachable_tile = current_board.get_tile_grid()[6][5]
    current_tile = sample_seeded_game_state.get_board().get_tile_by_position(current_tile_pos)
    # validate that reachable tile is reachable using previously tested reachable_tiles method
    assert reachable_tile in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert sample_seeded_game_state.can_active_player_reach_given_tile(reachable_tile)


def test_player_can_not_reach_tile_right(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile_pos = current_player.get_current_position()
    unreachable_tile = current_board.get_tile_grid()[5][6]
    current_tile = sample_seeded_game_state.get_board().get_tile_by_position(current_tile_pos)
    assert not unreachable_tile.has_path(Direction.Left)
    # validate that reachable tile is not reachable using previously tested reachable_tiles method
    assert unreachable_tile not in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert not sample_seeded_game_state.can_active_player_reach_given_tile(unreachable_tile)


def test_player_can_reach_tile_left(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile_pos = current_player.get_current_position()
    reachable_tile = current_board.get_tile_grid()[5][4]
    current_tile = sample_seeded_game_state.get_board().get_tile_by_position(current_tile_pos)
    # validate that reachable tile is reachable using previously tested reachable_tiles method
    assert reachable_tile in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert sample_seeded_game_state.can_active_player_reach_given_tile(reachable_tile)


# verifies can_active_player_reach_given_tile throws an exception when no players are in the game
def test_player_can_reach_tile_no_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        current_board = sample_seeded_game_state.get_board()
        unreachable_tile = current_board.get_tile_grid()[2][2]
        sample_seeded_game_state.can_active_player_reach_given_tile(unreachable_tile)
    assert str(error_message.value) == "No players to check"


def test_player_can_reach_tile_removed_all_players(sample_seeded_game_state):
    with pytest.raises(ValueError) as error_message:
        current_board = sample_seeded_game_state.get_board()
        unreachable_tile = current_board.get_tile_grid()[0][0]
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.add_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.kick_out_active_player()
        sample_seeded_game_state.can_active_player_reach_given_tile(unreachable_tile)
    assert str(error_message.value) == "No players to check"


# ----- Test slide Method -----
# Test that the slide method adjusts the players' positions if needed, testing the slide method itself
# is done on the board
def test_slide_does_not_move_stationary_players(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    pre_slide_positions = {}
    for player in sample_seeded_game_state.get_players():
        pre_slide_positions[player] = (player.get_current_position())
    sample_seeded_game_state.slide_and_insert(0, Direction.Down)
    for player in sample_seeded_game_state.get_players():
        assert player.get_current_position() == pre_slide_positions[player]


def test_slide_bumps_player_on_edge(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player_one = sample_seeded_game_state.get_players()[0]
    edge_tile = sample_seeded_game_state.get_board().get_tile_grid()[6][0]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    edge_tile_pos = sample_seeded_game_state.get_board().get_position_by_tile(edge_tile)
    player_one.set_current_position(edge_tile_pos)
    assert player_one.get_current_position() == edge_tile_pos
    sample_seeded_game_state.slide_and_insert(0, Direction.Down)
    next_tile_pos = sample_seeded_game_state.get_board().get_position_by_tile(next_tile)
    assert player_one.get_current_position() == next_tile_pos


def test_slide_bumps_two_players_on_edge(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player_one = sample_seeded_game_state.get_players()[0]
    player_two = sample_seeded_game_state.get_players()[1]
    player_three = sample_seeded_game_state.get_players()[2]
    edge_tile = sample_seeded_game_state.get_board().get_tile_grid()[2][6]
    unbumped_tile = sample_seeded_game_state.get_board().get_tile_grid()[1][5]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    edge_tile_pos = sample_seeded_game_state.get_board().get_position_by_tile(edge_tile)
    edge_tile_pos_two = sample_seeded_game_state.get_board().get_position_by_tile(edge_tile)
    unbumped_tile_pos = sample_seeded_game_state.get_board().get_position_by_tile(unbumped_tile)
    player_one.set_current_position(edge_tile_pos)
    player_two.set_current_position(unbumped_tile_pos)
    player_three.set_current_position(edge_tile_pos_two)
    assert player_one.get_current_position() == edge_tile_pos
    assert player_two.get_current_position() == unbumped_tile_pos
    assert player_three.get_current_position() == edge_tile_pos
    sample_seeded_game_state.slide_and_insert(2, Direction.Right)
    next_tile_pos = sample_seeded_game_state.get_board().get_position_by_tile(next_tile)
    assert player_one.get_current_position() == next_tile_pos
    assert player_two.get_current_position() == unbumped_tile_pos
    assert player_three.get_current_position() == next_tile_pos


# ----- Tests for change_active_player_turn ------
def test_change_active_player_turn_not_at_end(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    assert sample_seeded_game_state.get_active_player_index() == 0
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 1


def test_change_active_player_turn_at_end(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    assert sample_seeded_game_state.get_active_player_index() == 0
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 1
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 2
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 3
    sample_seeded_game_state.change_active_player_turn()
    assert sample_seeded_game_state.get_active_player_index() == 0


# ----- Test is_active_player_at_goal Method -----
# verifies the method returns true when the active player is at their home Position
def test_is_active_player_at_home(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    assert sample_seeded_game_state.is_active_player_at_home()


def test_is_active_player_not_at_home(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    active_player = sample_seeded_game_state.get_players()[0]
    goal_position = active_player.get_goal_position()
    sample_seeded_game_state.move_active_player_to(goal_position)
    assert not sample_seeded_game_state.is_active_player_at_home()


# ----- Test the move_active_player_to method -----
# validates that the move active player moves the currently active player to the specified location
def test_move_active_player_to_moves_active(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    active_player = sample_seeded_game_state.get_players()[0]
    assert active_player.get_current_position() == Position(5, 5)
    sample_seeded_game_state.move_active_player_to(Position(0, 4))
    assert active_player.get_current_position() == Position(0, 4)


def test_move_active_player_to_moves_active_two(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    active_player = sample_seeded_game_state.get_players()[0]
    assert active_player.get_current_position() == Position(5, 5)
    sample_seeded_game_state.move_active_player_to(Position(6, 6))
    assert active_player.get_current_position() == Position(6, 6)


def test_move_active_player_to_does_not_move_inactive(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    non_active_player_one = sample_seeded_game_state.get_players()[1]
    non_active_player_two = sample_seeded_game_state.get_players()[2]
    assert non_active_player_one.get_current_position() == Position(1, 1)
    assert non_active_player_two.get_current_position() == Position(1, 3)
    sample_seeded_game_state.move_active_player_to(Position(6, 6))
    assert non_active_player_one.get_current_position() == Position(1, 1)
    assert non_active_player_two.get_current_position() == Position(1, 3)


# ----- Test active_player_has_reached_goal ---------
def test_active_player_has_reached_goal(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    sample_seeded_game_state.is_active_player_at_goal()
    assert sample_seeded_game_state.active_player_has_reached_goal()


def test_active_player_has_not_reached_goal_one(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    assert not sample_seeded_game_state.active_player_has_reached_goal()
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    sample_seeded_game_state.is_active_player_at_goal()
    assert sample_seeded_game_state.active_player_has_reached_goal()


def test_active_player_has_not_reached_goal_two(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player = sample_seeded_game_state.get_players()[sample_seeded_game_state.get_active_player_index()]
    sample_seeded_game_state.move_active_player_to(player.get_goal_position())
    sample_seeded_game_state.is_active_player_at_goal()
    sample_seeded_game_state.change_active_player_turn()
    assert not sample_seeded_game_state.active_player_has_reached_goal()


# ---- Test get_closest_player_to_victory ---------
def test_get_closest_player_to_victory_no_goals_start(sample_seeded_game_state_from_players, player_one,
                                                      player_two, player_three):
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_one, player_three]


def test_get_closest_player_to_victory_no_goals_moved(sample_seeded_game_state_from_players, player_one,
                                                      player_two, player_three):
    player_one.set_current_position(Position(4, 6))
    player_two.set_current_position(Position(0, 0))
    player_three.set_current_position(Position(5, 3))
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_three]


def test_get_closest_player_to_victory_at_goal_moved(sample_seeded_game_state_from_players, player_one,
                                                     player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(2, 0))
    player_three.set_current_position(Position(3, 3))
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_one]


def test_get_closest_player_to_victory_at_goal_moved_two(sample_seeded_game_state_from_players, player_one,
                                                         player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(2, 0))
    player_three.set_current_position(Position(1, 1))
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_one]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached(sample_seeded_game_state_from_players, player_one,
                                                                      player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(3, 3))
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    sample_seeded_game_state_from_players.change_active_player_turn()
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_one]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached_two(sample_seeded_game_state_from_players,
                                                                          player_one,
                                                                          player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(2, 5))
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    sample_seeded_game_state_from_players.change_active_player_turn()
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    player_two.set_current_position(Position(3, 4))
    assert sample_seeded_game_state_from_players.get_closest_players_to_victory() == [player_two]


def test_get_closest_player_to_victory_at_goal_multiple_goals_reached_three(sample_seeded_game_state_from_players,
                                                                            player_one,
                                                                            player_two, player_three):
    player_one.set_current_position(Position(3, 1))
    player_two.set_current_position(Position(5, 5))
    player_three.set_current_position(Position(6, 0))
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    sample_seeded_game_state_from_players.change_active_player_turn()
    sample_seeded_game_state_from_players.is_active_player_at_goal()
    player_two.set_current_position(Position(2, 3))
    player_one.set_current_position(Position(4, 1))
    assert player_one in sample_seeded_game_state_from_players.get_closest_players_to_victory()
    assert player_two in sample_seeded_game_state_from_players.get_closest_players_to_victory()
    assert player_three not in sample_seeded_game_state_from_players.get_closest_players_to_victory()


def test_get_closest_player_to_victory_no_players(sample_seeded_game_state):
    assert len(sample_seeded_game_state.get_players()) == 0
    assert sample_seeded_game_state.get_closest_players_to_victory() == []
