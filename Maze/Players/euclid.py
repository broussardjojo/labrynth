from typing import List, Iterator

from .base_strategy import BaseStrategy
from ..Common.abstract_state import AbstractState
from ..Common.board import Board
from ..Common.position import Position
from ..Common.utils import get_euclidean_distance_between


class Euclid(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """

    def get_goals(self, state: AbstractState, primary_goal: Position) -> Iterator[Position]:
        """
        Creates an iterator of the immediate and alternative goals for the active player, in order of their preference.

        In this implementation, the ordering is first the immediate goal, then all positions ordered by Euclidean
        distance from the primary_goal, with ties broken according to minimum row, with ties broken according to minimum
        column.
        :param state: The current state of the game for the active players to look for goals on.
        :param primary_goal: The position of the highest priority goal - this should either be a position with the
            currently sought out gems on it, or the position of the active players' home if they have picked up all
            their goals.
        :return:  an ordered iterable of goal positions for the active player to try to reach on this move.
        """
        yield primary_goal

        # Add all non-primary goal tiles to a list to then sort
        alternative_goals: List[Position] = []
        for row in range(state.get_board().get_height()):
            for col in range(state.get_board().get_width()):
                pos = Position(row, col)
                if pos != primary_goal:
                    alternative_goals.append(pos)

        # Sort alternative goals
        alternative_goals.sort(key=lambda p: (get_euclidean_distance_between(p, primary_goal),
                                                p.get_row(),
                                                p.get_col()))

        yield from alternative_goals




    def possible_next_target_positions(self, board: Board) -> bool:
        """
        Method to determine if there are any unchecked positions left
        :param board: a Board representing the board to check positions on
        :return: True if there are any unchecked positions, otherwise false
        """
        return not len(super().get_checked_positions()) == board.get_height() ** 2

    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
        """
        Method to determine the next target Position according to the Euclid strategy, first the goal Position, then
        the Positions from top left to bottom right row by row
        :param original_target: a Position representing the original goal tile to be reached
        :param board: A Board to get potential target Positions from
        :return: A Position representing the next target position to check
        :raises: ValueError if there are no Positions left to check
        """
        if len(super().get_checked_positions()) == 0:
            return original_target
        first_unchecked_position = self.__get_first_unchecked(board)
        min_distance = get_euclidean_distance_between(first_unchecked_position, original_target)
        min_position = first_unchecked_position
        for row in range(board.get_height()):
            for col in range(board.get_width()):
                potential_position = Position(row, col)
                euclidean_distance = get_euclidean_distance_between(potential_position, original_target)
                if euclidean_distance < min_distance and potential_position not in super().get_checked_positions():
                    min_position = potential_position
                    min_distance = euclidean_distance
        return min_position

    def __get_first_unchecked(self, board: Board) -> Position:
        """
        Gets the first unchecked position on the Board
        :param board: The Board to check positions on
        :return: a Position representing the first unchecked Position in lexicographical ordering
        :raises: ValueError if there are no positions left to check
        """
        for row in range(board.get_height()):
            for col in range(board.get_width()):
                if Position(row, col) not in super().get_checked_positions():
                    return Position(row, col)
        raise ValueError("Error: No Positions left to check")
