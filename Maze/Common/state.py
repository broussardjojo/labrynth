from random import choice
from typing import List

from board import Board
from player import Player
from tile import Tile
from direction import Direction


class State:
    """
    A State is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active
    Player.
    """

    def __init__(self, board: Board):
        """
        A constructor for a State, taking in a Board which represents the board for a game of Labyrinth.
        :param board: a Board representing the board for a game of Labyrinth
        """
        self.__board = board
        self.__players = []
        self.__active_player_index = 0

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
            self.__board.get_next_tile().rotate(rotations)
        else:
            raise ValueError("Invalid degrees of rotations. Must be multiple of 90 degrees.")

    def get_board(self) -> Board:
        """
        Gets the __board in this State
        :return: a Board representing this State's board
        """
        return self.__board

    def add_player(self) -> None:
        """
        Adds a Player to this State's players.
        :return: None
        :raises: a ValueError if the game is full, meaning there are not enough Tiles left on this State's Board to give
        a new player home and goal Tiles.
        side effect: mutates this State's players with the addition of a new Player
        """
        if self.__are_available_home_and_goal_tile():
            new_player = Player(self.__generate_players_tile(want_home=True),
                                self.__generate_players_tile(want_home=False))
            self.__players.append(new_player)
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
        all_tiles = self.__board.get_tile_grid()
        for row in range(len(all_tiles)):
            for col in range(len(all_tiles[row])):
                if self.__board.check_stationary_position(row, col) \
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
        stationary_tiles = self.__board.get_all_stationary_tiles()
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
            if player.get_goal_tile() == potential_tile:
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
            if player.get_home_tile() == potential_tile:
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
        else:
            raise ValueError("No players to remove")

    def is_active_player_at_goal(self) -> bool:
        """
        Checks if the active player for this State is at their goal Tile.
        :return: True if the active player is at their goal Tile, otherwise False
        :raises: ValueError if there are no players in this State
        """
        if self.__players:
            return self.__players[self.__active_player_index].get_current_tile() == \
                   self.__players[self.__active_player_index].get_goal_tile()
        raise ValueError("No players to check")

    def can_active_player_reach_given_tile(self, target_tile: Tile) -> bool:
        """
        Determines if the active player can reach a given Tile
        :param target_tile: A Tile representing the potential destination to check against
        :return: True if the active player can reach the target, False otherwise
        :raises: ValueError if there are no players in this State
        """
        if self.__players:
            active_player = self.__players[self.__active_player_index]
            current_tile = active_player.get_current_tile()
            all_reachable = self.__board.reachable_tiles(current_tile)
            return target_tile in all_reachable
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
        next_tile = self.__board.get_next_tile()
        self.__board.slide_and_insert(index, direction)
        self.__adjust_slid_off_players(next_tile)

    def __adjust_slid_off_players(self, inserted_tile: Tile) -> None:
        """
        Move any players that may have been slid off of the board in the previous move onto the newly inserted Tile
        :return: None
        side effect: Potentially mutates the Players of this State if they get slid off this State's Board
        """
        for player in self.__players:
            if player.get_current_tile() == self.__board.get_next_tile():
                player.set_current_tile(inserted_tile)

    def get_players(self) -> List[Player]:
        """
        Gives the list of players for this State.
        :return: a List of Player which represents the players for this game State
        """
        return self.__players
