from typing import List
from .player import Player
from ..Common.state import State
from ..Common.board import Board


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
