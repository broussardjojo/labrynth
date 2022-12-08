from typing import List, Tuple, Dict, Optional

from Maze.Common.abstract_state import AbstractState
from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.redacted_state import RedactedState
from Maze.Common.referee_player_details import RefereePlayerDetails


class State(AbstractState[RefereePlayerDetails]):
    """
    A State is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active
    Player.
    """

    __player_to_goals_reached: Dict[RefereePlayerDetails, int]

    def __init__(self, board: Board, previous_moves: List[Tuple[int, Direction]], players: List[RefereePlayerDetails],
                 active_player_index: int):
        super().__init__(board, previous_moves, players, active_player_index)
        self.__player_to_goals_reached = {player: 0 for player in players}

    @classmethod
    def from_current_state(cls, board: Board, players: List[RefereePlayerDetails],
                           previous_moves: List[Tuple[int, Direction]]) -> "State":
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
    def from_board_and_players(cls, selected_board: Board, list_of_players: List[RefereePlayerDetails]) -> "State":
        """
        A constructor for a State, taking in a Board and a list of players and creating a state with no previous moves.
        :param selected_board: a Board representing the game board to use in this state
        :param list_of_players:  a List of Players representing the current players in the game
        :return: an instance of a State
        """
        active_player_index = 0
        return cls(selected_board, [], list_of_players, active_player_index)

    def kick_out_active_player(self) -> None:
        """
        Removes the currently active player from this State's list of players.
        :return: None
        side effect: mutates this State's list of players
        """
        if self._players:
            kicked_player = self._players.pop(self._active_player_index)
            self.__player_to_goals_reached.pop(kicked_player)
            if self._active_player_index >= len(self._players):
                self._active_player_index = 0
        else:
            raise ValueError("No players to remove")

    def is_active_player_at_goal(self) -> bool:
        """
        Checks if the active player for this State is at their goal Position.
        :return: True if the active player is at their goal Position, otherwise False
        :raises: ValueError if there are no players in this State
        """
        if self._players:
            active_player = self.get_active_player()
            next_goal_position = (active_player.get_goal_position())
            return active_player.get_current_position() == next_goal_position
        raise ValueError("No players to check")

    def update_active_player_goals_reached(self) -> bool:
        """
        adds 1 to the player's __player_to_goals_reached value if they are at their goal
        :return: True if the active player is at their goal Position, otherwise False
        """
        if self.is_active_player_at_goal() and not self.is_active_player_at_ultimate_goal():
            self.__player_to_goals_reached[self.get_active_player()] += 1
            return True
        return False

    def is_active_player_at_ultimate_goal(self) -> bool:
        """
        Checks if the active player for this State is has won (i.e. has reached two goals, their treasure
        Position followed by their home Position).
        :return: True if the active player has won, otherwise False
        :raises: ValueError if there are no players in this State
        """
        if self._players:
            active_player = self.get_active_player()
            return active_player.is_goal_ultimate() and self.is_active_player_at_goal()
        raise ValueError("No players to check")

    def is_active_player_at_home(self) -> bool:
        """
        Checks if the active player for this State is at their home Position.
        :return: True if the active player is at their goal Position, otherwise False
        :raises: ValueError if there are no players in this State
        """
        if self._players:
            active_player = self.get_active_player()
            return active_player.get_current_position() == active_player.get_home_position()
        raise ValueError("No players to check")

    def change_active_player_turn(self) -> None:
        """
        Change the active player's turn
        :return: None
        """
        if self._active_player_index < len(self._players) - 1:
            self._active_player_index += 1
        else:
            self._active_player_index = 0

    def active_player_has_reached_goal(self) -> bool:
        """
        Checks if the active player has ever reached their goal position
        :return: True if the active player for this State has ever reached their goal position, otherwise False
        """
        return self.__player_to_goals_reached[self.get_active_player()] > 0

    def get_closest_players_to_victory(self, did_active_player_move: bool) -> List[RefereePlayerDetails]:
        """
        A method to get the player or players who are closest to victory (either the players that have reached their
        goal and are closest to home or, if no players have reached their goal, the players closest to reaching their
        goal)

        Note: If the game ends because someone reached their home, this function must be called with the same active
            player that ended the game.
        :param did_active_player_move:
        :return: A list of Players representing the winning Players
        """
        if not self._players:
            return []
        players_at_max_goals = self.__get_players_at_max_goals()
        player_distance_pairs = self.__get_player_distances_to_next_goal(players_at_max_goals)
        closest_players = self.__get_closest_players_to_next_goal(player_distance_pairs)
        # Edge case for if multiple players have the same number of goals and the same minimum distance to next goal,
        # the winner should be the player who ended the game.
        should_prefer_active_player = did_active_player_move and self.is_active_player_at_ultimate_goal()
        if should_prefer_active_player and self.get_active_player() in closest_players:
            return [self.get_active_player()]
        return closest_players

    def __get_players_at_max_goals(self) -> List[RefereePlayerDetails]:
        """
        Return all players who have the highest amount of goals reached.
        :return: A list of RefereePlayerDetails.
        """
        max_goals_reached = max(self.__player_to_goals_reached.values())
        players_at_max_goals = [player for player, num_goals in self.__player_to_goals_reached.items()
                                if num_goals == max_goals_reached]
        return players_at_max_goals

    def __get_closest_players_to_next_goal(
        self,
        possible_winners: List[Tuple[RefereePlayerDetails, int]]
    ) -> List[RefereePlayerDetails]:
        """
        A method to get the closest players to either their goal or their home
        :param possible_winners: A list of Tuple[RefereePlayerDetails, int] representing players eligible to win and
            their squared distance to their next goal.
        :return: list of the players who share the same minimum squared distance to their goal
        """
        min_distance = min(distance for _, distance in possible_winners)
        players_at_min_distance = [player for player, distance in possible_winners if distance == min_distance]
        return players_at_min_distance

    def __get_player_distances_to_next_goal(
        self,
        players: List[RefereePlayerDetails]
    ) -> List[Tuple[RefereePlayerDetails, int]]:
        """
        Returns the SQUARED distance of each player in the given list to their next goal.
        :return: A list of Tuple[RefereePlayerDetails, int] representing the player and their squared distance
            to their next goal.
        """
        player_distances = [(player, player.get_euclidean_distance_from_current_to_goal()) for player in players]
        return player_distances

    def copy_redacted(self, active_player_index: Optional[int] = None) -> RedactedState:
        """
        Creates a copy of this state without access to any player secrets.
        :param active_player_index: An int representing the active player index to copy with, or None to use the
        State's active player index
        :return: A RedactedState
        """
        active_index_for_copy = self._active_player_index
        if active_player_index is not None:
            active_index_for_copy = active_player_index
        return RedactedState(self._board,
                             self._previous_moves,
                             [player.copy_without_secrets() for player in self._players],
                             active_player_index=active_index_for_copy)
