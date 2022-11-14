from abc import ABC
from typing import List, Tuple, TypeVar, Generic

from .board import Board
from .direction import Direction
from .position import Position
from .position_transition_map import PositionTransitionMap
from Maze.Common.player_details import PlayerDetails

TPlayer = TypeVar("TPlayer", bound=PlayerDetails)


class AbstractState(ABC, Generic[TPlayer]):
    """
    Base class for a State, containing only methods that both players and referees should have
    """

    _board: Board
    _players: List[TPlayer]
    _previous_moves: List[Tuple[int, Direction]]
    _active_player_index: int

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]], players: List[TPlayer],
                 active_player_index: int):
        """
        A constructor for superclasses of AbstractState, taking in a Board and creating an empty game state with no players
        :param board: a Board representing the game board to use in this state
        :param players: a List of Players representing the current players in the game
        :param previous_moves: a Tuple (int, Direction) representing the previous slide action
        :param active_player_index: an int representing the index of the next player in players who will take a turn
        :return: an instance of a State
        """
        self._board = board
        self._previous_moves = previous_moves.copy()
        self._players = players.copy()
        self._active_player_index = active_player_index

    def get_board(self) -> Board:
        """
        Gets the __board in this State
        :return: a Board representing this State's board
        """
        return self._board

    def get_all_previous_non_passes(self) -> List[Tuple[int, Direction]]:
        """
        Returns a list of all the previous slides and inserts.
        :return: a list of (int, Direction) representing all the previous slides and inserts
        """
        return self._previous_moves

    def get_players(self) -> List[TPlayer]:
        """
        Gives the list of players for this State.
        :return: a List of Player which represents the players for this game State
        """
        return self._players

    def get_active_player_index(self) -> int:
        """
        Getter for the __active_player_index
        :return: An int representing the current active player's index in the list of players
        """
        return self._active_player_index

    def get_active_player_position(self) -> Position:
        """
        A method to get the current position of the active player
        :return: a Position representing the current location of the active player
        """
        return self.get_active_player().get_current_position()

    def get_active_player(self) -> TPlayer:
        """
        Returns the active player
        :return: A Player
        :raises: IndexError if there are no players left
        """
        return self._players[self._active_player_index]

    def rotate_spare_tile(self, degrees: int) -> None:
        """
        Rotates the spare tile of this State's Board some multiple of 90 degrees.
        :param degrees: int representing the number of degrees to rotate the spare tile (clockwise)
        :return: None
        :raises: ValueError if given degrees is not a multiple of 90
        side effect: mutates the spare tile of this State's Board by changing the Tile's Shape paths
        """
        if degrees % 90 == 0:
            rotations = int(degrees / 90)
            self._board.get_next_tile().rotate(rotations)
        else:
            raise ValueError("Invalid degrees of rotations. Must be multiple of 90 degrees.")

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
        position_transitions = self._board.slide_and_insert(index, direction)
        self._adjust_all_players(position_transitions)
        self._previous_moves.append((index, direction))

    def _adjust_all_players(self, transitions: PositionTransitionMap) -> None:
        """
        Move any players that have been slid during the previous slide move. Players that may have been slid off of the
        board in the previous move are placed onto the newly inserted Tile
        :param transitions: a PositionTransitionMap representing the mapping of previous positions to new positions
        :return: None
        side effect: Potentially mutates the Players of this State if they get slid on this State's Board
        """
        for player in self.get_players():
            old_position = player.get_current_position()
            if old_position in transitions.updated_positions:
                player.set_current_position(transitions.updated_positions[old_position])
            elif old_position == transitions.removed_position:
                player.set_current_position(transitions.inserted_position)

    def move_active_player_to(self, position_to_move_to: Position) -> None:
        """
        Method to move the currently active player to the specified position
        NOTE: Assuming only trusted users have access to this class and this method meaning only valid moves can be made
        :param position_to_move_to: a Position representing the destination to move a player to
        :return: None
        Side Effect: Mutates the currently active Player
        """
        self.get_active_player().set_current_position(position_to_move_to)