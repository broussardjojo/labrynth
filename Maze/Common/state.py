from random import choice
from typing import List, Tuple

from .board import Board
from ..Players.player import Player
from .tile import Tile
from .direction import Direction
from .utils import ALL_NAMED_COLORS

from .position import Position
from ..Players.riemann import Riemann
from .observableState import ObservableState


class State(ObservableState):
    """
    A State is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active
    Player.
    """

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]], players: List[Player],
                 active_player_index: int):
        super().__init__(board)
        self.__previous_moves = previous_moves
        self.__players = players
        self.__active_player_index = active_player_index
        self.__players_reached_goal = set()

    @classmethod
    def from_random_state(cls, board: Board):
        """
        A constructor for a State, taking in a Board and creating an empty game state with no players
        :param board: a Board representing the game board to use in this state
        :return: an instance of a State
        """
        previous_moves = []
        players = []
        active_player_index = 0
        return cls(board, previous_moves, players, active_player_index)

    @classmethod
    def from_current_state(cls, board: Board, players: List[Player], previous_move: Tuple[int, Direction]):
        """
        A constructor for a State, taking in a Board and creating an empty game state with no players
        :param board: a Board representing the game board to use in this state
        :param players: a List of Players representing the current players in the game
        :param previous_move: a Tuple containing an int representing the previous slide index and a Direction
        representing the previous slide Direction
        :return: an instance of a State
        """
        previous_moves = [previous_move]
        active_player_index = 0
        return cls(board, previous_moves, players, active_player_index)

    @classmethod
    def from_board_and_players(cls, selected_board: Board, list_of_players: List[Player]):
        """
        A constructor for a State, taking in a Board and a list of players and creating a state with no previous moves.
        :param selected_board: a Board representing the game board to use in this state
        :param list_of_players:  a List of Players representing the current players in the game
        :return: an instance of a State
        """
        previous_moves = []
        active_player_index = 0
        return cls(selected_board, previous_moves, list_of_players, active_player_index)

    def rotate_spare_tile(self, degrees: int) -> None:
        """
        Rotates the spare tile of this State's Board some multiple of 90 degrees.
        :param degrees: int representing the number of degrees to rotate the spare tile
        :return: None
        :raises: ValueError if given degrees is not a multiple of 90
        side effect: mutates the spare tile of this State's Board by changing the Tile's Shape paths
        """
        if degrees % 90 == 0:
            rotations = int(degrees / 90)
            super().get_board().get_next_tile().rotate(rotations)
        else:
            raise ValueError("Invalid degrees of rotations. Must be multiple of 90 degrees.")

    def add_player(self) -> None:
        """
        Adds a Player to this State's players.
        :return: None
        :raises: a ValueError if the game is full, meaning there are not enough Tiles left on this State's Board to give
        a new player home and goal Tiles.
        side effect: mutates this State's players with the addition of a new Player
        """
        if self.__are_available_home_and_goal_tile():
            home_tile = self.__generate_players_tile(want_home=True)
            goal_tile = self.__generate_players_tile(want_home=False)
            goal_position = super().get_board().get_position_by_tile(goal_tile)
            new_player = Player.from_goal_home_color_strategy(goal_position,
                                                              super().get_board().get_position_by_tile(home_tile),
                                                              self.__get_unique_color(), Riemann(goal_position))
            self.get_players().append(new_player)
        else:
            raise ValueError("Game is full, no more players can be added")

    def __are_available_home_and_goal_tile(self) -> bool:
        """
        Checks if there is at least one Tile on this State's Board that is available. A Tile is available if it is
        stationary, meaning it does not slide, and it is not associated with any other Players.
        ASSUMPTION: The home Tile and goal Tile for a Player can be the same, but the home Tile for a Player must be
        different than the home Tile for another Player of this State
        :return: True if there is at least one available Tile of each type (home and goal) on this State's Board, False
        otherwise
        """
        all_tiles = super().get_board().get_tile_grid()
        for row in range(len(all_tiles)):
            for col in range(len(all_tiles[row])):
                if super().get_board().check_stationary_position(row, col) \
                        and self.__tile_is_available_as_goal(all_tiles[row][col]) \
                        and self.__tile_is_available_as_home(all_tiles[row][col]):
                    return True
        return False

    def __generate_players_tile(self, want_home) -> Tile:
        """
        Generates a Tile that is stationary. A Tile is stationary if it does not slide.
        :param: want_home a boolean representing if the Tile being generated will be used as a home Tile or goal Tile.
        If it will be used as a home Tile, want_home is True, if it will be used as a goal Tile, want_home is False
        :return: A Tile which represents a potential home for a Player
        :raises: a ValueError if there are no Tiles left on this State's Board that are stationary
        """
        stationary_tiles = super().get_board().get_all_stationary_tiles()
        while stationary_tiles:
            potential_tile = choice(stationary_tiles)
            if want_home:
                if self.__tile_is_available_as_home(potential_tile):
                    return potential_tile
            else:
                if self.__tile_is_available_as_goal(potential_tile):
                    return potential_tile
            stationary_tiles.remove(potential_tile)
        raise ValueError("No Stationary Tiles")

    def __tile_is_available_as_goal(self, potential_tile: Tile) -> bool:
        """
        Checks if the given Tile is available to be a goal Tile. A Tile is available as a goal if it is not a goal tile
        for a Player of this State.
        :param potential_tile: a Tile on this State's Board, represents a potential goal Tile
        :return: True if the Tile is available as a goal Tile, False otherwise
        """
        for player in self.__players:
            if super().get_board().get_tile_by_position(player.get_goal_position()) == potential_tile:
                return False
        return True

    def __tile_is_available_as_home(self, potential_tile: Tile) -> bool:
        """
        Checks if the given Tile is available as a home Tile. A Tile is available to be a home Tile if it is not a home
        tile for a Player of this State.
        :param potential_tile: a Tile on this State's Board, represents a potential home Tile
        :return: True if the Tile is available as a home Tile, False otherwise
        """
        for player in self.__players:
            if player.get_home_position() == potential_tile:
                return False
        return True

    def kick_out_active_player(self) -> None:
        """
        Removes the currently active player from this State's list of players.
        :return: None
        side effect: mutates this State's list of players
        """
        if self.__players:
            self.__players.pop(self.__active_player_index)
            if self.__active_player_index >= len(self.__players):
                self.__active_player_index = 0
        else:
            raise ValueError("No players to remove")

    def is_active_player_at_goal(self) -> bool:
        """
        Checks if the active player for this State is at their goal Position.
        :return: True if the active player is at their goal Position, otherwise False
        :raises: ValueError if there are no players in this State
        side effect: adds active player to Set of __players_reached_goal if they are at their goal
        """
        if self.__players:
            active_player = self.__players[self.__active_player_index]
            if active_player.get_current_position() == active_player.get_goal_position():
                self.__players_reached_goal.add(active_player)
                return True
            return False
        raise ValueError("No players to check")

    def slide_and_insert(self, index: int, direction: Direction) -> None:
        """
        Slides this State's board at the given index in the given direction
        :param index: an int representing the row or column to slide
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: None
        :raises: ValueError if the given index is not eligible to slide
        side effect: mutates __board by changing the Board's __tile_grid and __next_tile. Potentially mutates the
        Players of this State if they get slid off this State's Board
        """
        super().get_board().slide_and_insert(index, direction)
        self.__adjust_all_players(index, direction)
        self.__previous_moves.append((index, direction))

    def __adjust_all_players(self, slide_index: int, slide_direction: Direction) -> None:
        """
        Move any players that have been slid during the previous slide move. Players that may have been slid off of the
        board in the previous move are placed onto the newly inserted Tile
        :return: None
        side effect: Potentially mutates the Players of this State if they get slid on this State's Board
        """
        for player in self.__players:
            new_position = self.__adjust_player_position_in_bound(player, slide_index, slide_direction)
            player.set_current_position(new_position)

    def __adjust_player_position_in_bound(self, player: Player, slide_index: int,
                                          slide_direction: Direction) -> Position:
        """
        Adjusts a player of this State's position on this State's Board after a slide. If a slide results in a player
        having a Position not on the Board, adjusts the player's position to be on the Board.
        :param player: a Player representing the player whose position is being adjusted
        :param slide_index: an int representing the row or column being slide
        :param slide_direction: a Direction representing the direction the row or column is being slid
        :return: a Position representing the player's new position on the Board
        """
        player_row = player.get_current_position().get_row()
        player_col = player.get_current_position().get_col()
        max_valid_pos = len(super().get_board().get_tile_grid()) - 1
        if slide_direction == Direction.Up:
            if slide_index == player_col:
                new_row = player_row - 1 if player_row > 0 else max_valid_pos
                return Position(new_row, player_col)
        elif slide_direction == Direction.Down:
            if slide_index == player_col:
                new_row = player_row + 1 if player_row < max_valid_pos else 0
                return Position(new_row, player_col)
        elif slide_direction == Direction.Left:
            if slide_index == player_row:
                new_col = player_col - 1 if player_col > 0 else max_valid_pos
                return Position(player_row, new_col)
        else:
            if slide_index == player_row:
                new_col = player_col + 1 if player_col < max_valid_pos else 0
                return Position(player_row, new_col)
        return Position(player_row, player_col)

    def get_players(self) -> List[Player]:
        """
        Gives the list of players for this State.
        :return: a List of Player which represents the players for this game State
        """
        return self.__players

    def can_active_player_reach_given_tile(self, target_tile: Tile) -> bool:
        """
        Determines if the active player can reach a given Tile
        :param target_tile: A Tile representing the potential destination to check against
        :return: True if the active player can reach the target, False otherwise
        :raises: ValueError if there are no players in this State
        """
        if self.__players:
            active_player = self.__players[self.__active_player_index]
            current_tile_position = active_player.get_current_position()
            target_tile_position = super().get_board().get_position_by_tile(target_tile)
            return self.__can_reach_position_from_given_position(current_tile_position, target_tile_position)
        raise ValueError("No players to check")

    def __can_reach_position_from_given_position(self, start_position, end_position):
        """
        Method to check if a given position can be reached from another given position on this State's Board
        :param start_position: Position to begin from
        :param end_position: Position to end at
        :return: True if there is a path from the start Position to the end Position in the current condition of the
        Board
        """
        current_tile = super().get_board().get_tile_by_position(start_position)
        target_tile = super().get_board().get_tile_by_position(end_position)
        all_reachable = super().get_board().reachable_tiles(current_tile)
        return target_tile in all_reachable

    def get_active_player_index(self) -> int:
        """
        Getter for the __active_player_index
        :return: An int representing the current active player's index in the list of players
        """
        return self.__active_player_index

    def is_active_player_at_home(self) -> bool:
        """
        Checks if the active player for this State is at their home Position.
        :return: True if the active player is at their goal Position, otherwise False
        :raises: ValueError if there are no players in this State
        """
        if self.__players:
            active_player = self.__players[self.__active_player_index]
            return active_player.get_current_position() == active_player.get_home_position()
        raise ValueError("No players to check")

    def change_active_player_turn(self) -> None:
        """
        Change the active player's turn
        :return: None
        """
        if self.__active_player_index < len(self.__players) - 1:
            self.__active_player_index += 1
        else:
            self.__active_player_index = 0

    def __get_unique_color(self) -> str:
        """
        Gets a unique color for a Player from the list of named colors
        :return: A string representing a color for a player to use
        :raises: ValueError if there are no named colors available for Players to use
        """
        currently_used_colors = [player.get_color() for player in self.__players]
        for color in ALL_NAMED_COLORS:
            if color not in currently_used_colors:
                return color
        raise ValueError("No colors left")

    def move_active_player_to(self, position_to_move_to: Position) -> None:
        """
        Method to move the currently active player to the specified position
        NOTE: Assuming only trusted users have access to this class and this method meaning only valid moves can be made
        :param position_to_move_to: a Position representing the destination to move a player to
        :return: None
        Side Effect: Mutates the currently active Player
        """
        self.__players[self.__active_player_index].set_current_position(position_to_move_to)

    def active_player_has_reached_goal(self):
        """
        Checks if the active player has ever reached their goal position
        :return: True if the active player for this State has ever reached their goal position, otherwise False
        """
        return self.__players[self.__active_player_index] in self.__players_reached_goal

    def get_last_non_pass(self) -> (int, Direction):
        """
        Returns the last move, namely, the last index and Direction the board was slid.
        :return: The index and Direction the board was slid during the last move. If there is no previous move, return
        arbitrary values garunteed not to interfere with game play
        """
        if len(self.__previous_moves) > 0:
            return self.__previous_moves[-1]
        return -1, Direction.Up

    def get_closest_players_to_victory(self):
        # TODO: write and test method
        pass
