from random import random, choice
from typing import List

from board import Board
from player import Player
from tile import Tile


class State:
    """
    A Board is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active Player.
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
        side effect: mutates the spare tile of this State's Board
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
        side effect: mutates this State's players
        """
        # if self.__are_available_home_and_goal_tiles():
        home_tile = self.__generate_players_tile()
        new_player = Player(home_tile, self.__generate_players_tile(), home_tile)
        self.__players.append(new_player)
        # else:
        #   raise ValueError("Game is full, no more players can be added")

    # def __are_available_home_or_goal_tile(self) -> bool:
    #     """
    #     Checks if there are at least one Tile on this State's Board that is available. A Tile is available if it is
    #     stationary, meaning it does not slide, and it is not associated with any other Players.
    #     :return: True if there are at least one available Tile, False otherwise
    #     """
    #     all_tiles = self.__board.get_tile_grid()
    #     for row in range(len(all_tiles)):
    #         for col in range(len(all_tiles[row])):
    #             if self.__board.check_stationary_position(row, col) \
    #                     and self.__tile_is_available(all_tiles[row][col]):
    #                 return True
    #     return False

    def __generate_players_tile(self) -> Tile:
        """
        Generates a Tile that is stationary. A Tile is stationary if it does not slide.
        :return: A Tile which represents a potential home for a Player
        :raises: a ValueError if there are no Tiles left on this State's Board that are stationary
        """
        stationary_tiles = self.__board.get_all_stationary_tiles()
        while stationary_tiles:
            return choice(stationary_tiles)
            # if self.__tile_is_available(potential_tile):
            #     return potential_tile
            # stationary_tiles.remove(potential_tile)
        raise ValueError("No Stationary Tiles")

    # def __tile_is_available(self, potential_tile: Tile) -> bool:
    #     """
    #     Checks if the given Tile is available. A Tile is available if it is not a goal or home tile for a Player of this
    #     State.
    #     :param potential_tile: a Tile on this State's Board, represents a potential goal or home tile
    #     :return: True if the Tile is available, False otherwise
    #     """
    #     for player in self.__players:
    #         if player.get_home_tile() == potential_tile:
    #             return False
    #         if player.get_goal_tile() == potential_tile:
    #             return False
    #     return True

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
        """
        if self.__players:
            return self.__players[self.__active_player_index].get_current_tile() == \
                   self.__players[self.__active_player_index].get_goal_tile()
        raise ValueError("No players to check")

    def get_players(self) -> List[Player]:
        """
        Gives the list of players for this State.
        :return: a List of Player which represents the players for this game State
        """

        return self.__players
