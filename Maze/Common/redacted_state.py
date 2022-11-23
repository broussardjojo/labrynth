from typing import List, Tuple

from Maze.Common.abstract_state import AbstractState
from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.player_details import PlayerDetails


class RedactedState(AbstractState[PlayerDetails]):
    """
    A RedactedState is a representation of a Labyrinth game game-state. A RedactedState has a Board, list of Players,
    and an active Player.
    """

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]], players: List[PlayerDetails],
                 active_player_index: int):
        """
        A constructor for an AbstractState, taking in a Board and creating an empty game state with no players
        :param board: a Board representing the game board to use in this state
        :param players: a List of Players representing the current players in the game
        :param previous_moves: a Tuple (int, Direction) representing the previous slide action
        :param active_player_index: an int representing the index of the next player in players who will take a turn
        :return: an instance of a State
        """
        super().__init__(board, previous_moves, players, active_player_index)

    @classmethod
    def from_current_state(cls, board: Board, players: List[PlayerDetails],
                           previous_moves: List[Tuple[int, Direction]]) -> "RedactedState":
        """
        A constructor for a State, which assumes that the first player in the given list will move next
        :param board: a Board representing the game board to use in this state
        :param players: a List of Players representing the current players in the game
        :param previous_moves: a Tuple containing an int representing the previous slide index and a Direction
        representing the previous slide Direction
        :return: an instance of a State
        """
        active_player_index = 0
        return cls(board, previous_moves, players, active_player_index)

    @classmethod
    def from_board_and_players(cls, selected_board: Board, list_of_players: List[PlayerDetails]) -> "RedactedState":
        """
        A constructor for a State, taking in a Board and a list of players and creating a state with no previous moves.
        :param selected_board: a Board representing the game board to use in this state
        :param list_of_players:  a List of Players representing the current players in the game
        :return: an instance of a State
        """
        active_player_index = 0
        return cls(selected_board, [], list_of_players, active_player_index)
