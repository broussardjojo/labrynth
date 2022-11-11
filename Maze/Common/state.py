from typing import List, Tuple

from .board import Board
from .position_transition_map import PositionTransitionMap
from ..Players.player import Player
from .direction import Direction
from .utils import ALL_NAMED_COLORS, get_euclidean_distance_between

from .position import Position
from .observableState import ObservableState


class State(ObservableState):
    """
    A State is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active
    Player.
    """

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]], players: List[Player],
                 active_player_index: int):
        super().__init__(board, previous_moves)
        self.__players = players
        self.__active_player_index = active_player_index
        self.__players_reached_goal = set()

    @classmethod
    def from_current_state(cls, board: Board, players: List[Player], previous_moves: List[Tuple[int, Direction]]):
        """
        A constructor for a State, taking in a Board and creating an empty game state with no players
        :param board: a Board representing the game board to use in this state
        :param players: a List of Players representing the current players in the game
        :param previous_moves: a Tuple containing an int representing the previous slide index and a Direction
        representing the previous slide Direction
        :return: an instance of a State
        """
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
        active_player_index = 0
        return cls(selected_board, [], list_of_players, active_player_index)

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
            active_player = self.get_active_player()
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
        position_transitions = self._board.slide_and_insert(index, direction)
        self.__adjust_all_players(position_transitions)
        self._previous_moves.append((index, direction))

    def __adjust_all_players(self, transitions: PositionTransitionMap) -> None:
        """
        Move any players that have been slid during the previous slide move. Players that may have been slid off of the
        board in the previous move are placed onto the newly inserted Tile
        :param transitions: a PositionTransitionMap representing the mapping of previous positions to new positions
        :return: None
        side effect: Potentially mutates the Players of this State if they get slid on this State's Board
        """
        for player in self.__players:
            old_position = player.get_current_position()
            if old_position in transitions.updated_positions:
                player.set_current_position(transitions.updated_positions[old_position])
            elif old_position == transitions.removed_position:
                player.set_current_position(transitions.inserted_position)

    def get_players(self) -> List[Player]:
        """
        Gives the list of players for this State.
        :return: a List of Player which represents the players for this game State
        """
        return self.__players

    def can_active_player_reach_position(self, target_position: Position) -> bool:
        """
        Determines if the active player can reach a given Tile
        :param target_position: A Tile representing the potential destination to check against
        :return: True if the active player can reach the target, False otherwise
        :raises: ValueError if there are no players in this State
        """
        if self.__players:
            active_player = self.get_active_player()
            current_tile_position = active_player.get_current_position()
            return self.__can_reach_position_from_position(current_tile_position, target_position)
        raise ValueError("No players to check")

    def __can_reach_position_from_position(self, start_position, end_position) -> bool:
        """
        Method to check if a given position can be reached from another given position on this State's Board
        :param start_position: Position to begin from
        :param end_position: Position to end at
        :return: True if there is a path from the start Position to the end Position in the current condition of the
        Board
        """
        all_reachable = self._board.reachable_tiles(end_position)
        return start_position in all_reachable

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
            active_player = self.get_active_player()
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
        self.get_active_player().set_current_position(position_to_move_to)

    def active_player_has_reached_goal(self) -> bool:
        """
        Checks if the active player has ever reached their goal position
        :return: True if the active player for this State has ever reached their goal position, otherwise False
        """
        return self.get_active_player() in self.__players_reached_goal

    def get_closest_players_to_victory(self) -> List[Player]:
        """
        A method to get the player or players who are closest to victory (either the players that have reached their
        goal and are closest to home or, if no players have reached their goal, the players closest to reaching their
        goal)
        :return: A list of Players representing the winning Players
        """
        if len(self.__players_reached_goal) > 0:
            return self.__get_closest_players_to_goal_or_home(list(self.__players_reached_goal), is_goal=False)
        return self.__get_closest_players_to_goal_or_home(self.__players, is_goal=True)

    def __get_closest_players_to_goal_or_home(self, possible_winners: List[Player], is_goal: bool):
        """
        A method to get the closest players to either their goal or their home
        :param possible_winners: A List of Players representing the players who are eligible to win the game
        :param is_goal: A bool that is True if the target destination to check against is the goal, False if it is the
        home
        :return: A list of Players representing the winning Players
        """
        closest_players = []
        current_min_distance = get_euclidean_distance_between(Position(0, 0),
                                                              Position(self._board.get_height(),
                                                                       self._board.get_width()))
        for player in possible_winners:
            if is_goal:
                player_distance = get_euclidean_distance_between(player.get_current_position(),
                                                                 player.get_goal_position())
            else:
                player_distance = get_euclidean_distance_between(player.get_current_position(),
                                                                 player.get_home_position())
            if player_distance < current_min_distance:
                current_min_distance = player_distance
                closest_players = [player]
            elif player_distance == current_min_distance:
                closest_players.append(player)
        return closest_players

    def get_active_player_position(self) -> Position:
        """
        A method to get the current position of the active player
        :return: a Position representing the current location of the active player
        """
        return self.get_active_player().get_current_position()

    def get_active_player(self):
        return self.__players[self.__active_player_index]
