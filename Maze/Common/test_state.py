import pytest
from board import Board
from state import State
from tile import Tile
from shapes import Line
from gem import Gem
from direction import Direction


@pytest.fixture
def seeded_board():
    return Board(seed=10)


@pytest.fixture
def seeded_spare_tile():
    return Tile(Line(0), Gem('emerald'), Gem('rhodonite'))


@pytest.fixture
def rotated_seeded_spare_tile():
    return Tile(Line(1), Gem('emerald'), Gem('rhodonite'))


@pytest.fixture
def sample_seeded_game_state(seeded_board):
    return State(seeded_board)


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
    goal_tile = active_player.get_goal_tile()
    active_player._Player__current_tile = goal_tile
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
def test_player_cannot_reach_current_tile(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_player = sample_seeded_game_state.get_players()[0]
    current_tile = current_player.get_current_tile()
    assert not sample_seeded_game_state.can_active_player_reach_given_tile(current_tile)


def test_player_can_reach_tile_above(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile = current_player.get_current_tile()
    reachable_tile = current_board.get_tile_grid()[4][5]
    # validate that reachable tile is reachable using previously tested reachable_tiles method
    assert reachable_tile in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert sample_seeded_game_state.can_active_player_reach_given_tile(reachable_tile)


def test_player_can_reach_tile_below(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile = current_player.get_current_tile()
    reachable_tile = current_board.get_tile_grid()[6][5]
    # validate that reachable tile is reachable using previously tested reachable_tiles method
    assert reachable_tile in current_board.reachable_tiles(current_tile)
    # assertion for new method
    assert sample_seeded_game_state.can_active_player_reach_given_tile(reachable_tile)


def test_player_can_not_reach_tile_right(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    current_board = sample_seeded_game_state.get_board()
    current_player = sample_seeded_game_state.get_players()[0]
    # Tile at location 5, 5, is cross shaped
    current_tile = current_player.get_current_tile()
    unreachable_tile = current_board.get_tile_grid()[5][6]
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
    current_tile = current_player.get_current_tile()
    reachable_tile = current_board.get_tile_grid()[5][4]
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
        pre_slide_positions[player] = (player.get_current_tile())
    sample_seeded_game_state.slide(0, Direction.Down)
    for player in sample_seeded_game_state.get_players():
        assert player.get_current_tile() == pre_slide_positions[player]


def test_slide_bumps_player_on_edge(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player_one = sample_seeded_game_state.get_players()[0]
    edge_tile = sample_seeded_game_state.get_board().get_tile_grid()[6][0]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    player_one.set_current_tile(edge_tile)
    assert player_one.get_current_tile() == edge_tile
    sample_seeded_game_state.slide(0, Direction.Down)
    assert player_one.get_current_tile() == next_tile


def test_slide_bumps_two_players_on_edge(sample_seeded_game_state):
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    sample_seeded_game_state.add_player()
    player_one = sample_seeded_game_state.get_players()[0]
    player_two = sample_seeded_game_state.get_players()[1]
    player_three = sample_seeded_game_state.get_players()[2]
    edge_tile = sample_seeded_game_state.get_board().get_tile_grid()[2][6]
    unbumped_tile = sample_seeded_game_state.get_board().get_tile_grid()[2][5]
    next_tile = sample_seeded_game_state.get_board().get_next_tile()
    player_one.set_current_tile(edge_tile)
    player_two.set_current_tile(unbumped_tile)
    player_three.set_current_tile(edge_tile)
    assert player_one.get_current_tile() == edge_tile
    assert player_two.get_current_tile() == unbumped_tile
    assert player_three.get_current_tile() == edge_tile
    sample_seeded_game_state.slide(2, Direction.Right)
    assert player_one.get_current_tile() == next_tile
    assert player_two.get_current_tile() == unbumped_tile
    assert player_three.get_current_tile() == next_tile
