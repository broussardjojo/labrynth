from typing import List
from .player import Player
from ..Common.state import State
from ..Common.board import Board
from ..Common.observableState import ObservableState
from ..Common.position import Position
from ..Common.utils import get_opposite_direction


class Referee:
    """
    A class representing a Referee for a game of Labyrinth. A referee is an arbiter of the game and is responsible for
    running the game to completion.
    # TODO: Document abnormal interactions referee now handles
    """

    def __init__(self, state: State):
        """
        Creates an instance of a Referee given a game State
        :param state: represents the game State this Referee will use to run the game
        """
        self.__game_state = state
        self.__cheater_players = []
        self.__winning_players = []
        self.__num_rounds = 0
        self.__all_player_goals = []
        self.__passed_players = []

    @classmethod
    def from_list_of_players(cls, list_of_players: List[Player]):
        """
        Creates an instance of a Referee given a list of players sorted in ascending order based on age
        :param list_of_players: represents the players of a game of Labyrinth sorted in ascending age order
        """
        selected_board = cls.get_proposed_board(list_of_players)
        game_state = State.from_board_and_players(selected_board, list_of_players)
        return cls(game_state)

    @staticmethod
    def get_proposed_board(list_of_players: List[Player]) -> Board:
        """
        Gets a Board from Players' proposals
        NOTE: this method is mainly defined for testing at this point, we will implement it fully when it is required
        :param list_of_players: the list of Players allowed to propose a Board
        :return: a randomly selected Board from the list of proposed Boards
        """
        return Board.from_random_board(seed=3)

    def run_game(self) -> (List[Player], List[Player]):
        self.__setup()
        while self.__game_not_over():
            active_player_index = self.__game_state.get_active_player_index()
            if active_player_index == 0:
                self.__num_rounds += 1
            active_player = self.__game_state.get_players()[active_player_index]
            observable_state = ObservableState(self.__game_state.get_board())
            proposed_move = active_player.take_turn(observable_state)
            if self.__is_valid_move(proposed_move):
                if not proposed_move.is_pass():
                    self.__passed_players = []
                    self.__game_state.rotate_spare_tile(proposed_move.get_spare_tile_rotation_degrees())
                    self.__game_state.slide_and_insert(proposed_move.get_slide_index(),
                                                       proposed_move.get_slide_direction())
                    self.__game_state.move_active_player_to(proposed_move.get_destination_position())
                    if self.__game_state.is_active_player_at_goal():
                        active_player.setup(active_player.get_home_position())
                else:
                    self.__passed_players.append(active_player)
                self.__game_state.change_active_player_turn()
        self.__inform_winning_players()
        return self.__winning_players, self.__cheater_players

    def __setup(self):
        for player in self.__game_state.get_players():
            observable_state = ObservableState(self.__game_state.get_board())
            player.setup(observable_state, self.__generate_unique_goal())

    def __generate_unique_goal(self) -> Position:
        tile_grid = self.__game_state.get_board().get_tile_grid()
        for row in range(len(tile_grid)):
            for col in range(len(tile_grid[row])):
                if self.__game_state.get_board().check_stationary_position(row, col):
                    potential_position = Position(row, col)
                    if potential_position not in self.__all_player_goals:
                        self.__all_player_goals.append(potential_position)
                        return potential_position
        raise ValueError("No Unique Goals Left")

    def __game_not_over(self) -> bool:
        """
        Returns whether the game is over or not. The game is considered over if the active player reaches their home
        position after visiting their goal position, the number of rounds reaches 1000, every player in a round
        passes, or there are 0 players left in the game.
        :return: True if the game is over, otherwise False
        """
        active_player = self.__game_state.get_players()[self.__game_state.get_active_player_index()]
        if self.__game_state.is_active_player_at_home() and self.__game_state.active_player_has_reached_goal():
            self.__winning_players = [active_player]
            return False
        if self.__num_rounds == 1000 or len(self.__passed_players) == len(self.__game_state.get_players()):
            self.__winning_players = self.__game_state.get_closest_players_to_victory()
            return False
        return len(self.__game_state.get_players()) > 0

    def __inform_winning_players(self) -> None:
        """
        Tells all winning players they have won the game
        :return: None
        """
        for player in self.__winning_players:
            player.won(True)

    def __is_valid_move(self, proposed_move):
        return self.__check_rotation(proposed_move.get_spare_tile_rotation_degrees()) \
               and self.__check_slide_and_insert(proposed_move.get_slide_index(), proposed_move.get_slide_direction()) \
               and self.__check_player_move(proposed_move)

    @staticmethod
    def __check_rotation(rotation_degrees):
        return rotation_degrees % 90 == 0

    def __check_slide_and_insert(self, slide_index, slide_direction):
        last_index, last_direction = self.__game_state.get_last_non_pass()
        if last_index == slide_index and last_direction == get_opposite_direction(slide_direction):
            return False
        return self.__game_state.get_board().can_slide(slide_index)

    def __check_player_move(self, proposed_move):
        # TODO: write and test method
        pass
