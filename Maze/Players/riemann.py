from typing import Iterator

from Maze.Players.base_strategy import BaseStrategy
from Maze.Common.abstract_state import AbstractState
from Maze.Common.board import Board
from Maze.Common.position import Position


class Riemann(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """

    def get_goals(self, state: AbstractState, primary_goal: Position) -> Iterator[Position]:
        """
        Creates an iterator of the immediate and alternative goals for the active player, in order of their preference.

        In this implementation, the ordering is first the immediate goal, then all positions based on (Row, Column)
        index.
        :param state: The current state of the game for the active players to look for goals on.
        :param primary_goal: The position of the highest priority goal - this should either be a position with the
            currently sought out gems on it, or the position of the active players' home if they have picked up all
            their goals.
        :return:  an ordered iterable of goal positions for the active player to try to reach on this move.
        """
        yield primary_goal
        for row in range(state.get_board().get_height()):
            for col in range(state.get_board().get_width()):
                pos = Position(row, col)
                if pos != primary_goal:
                    yield pos

    def possible_next_target_positions(self, board: Board) -> bool:
        """
        Method to determine if there are any unchecked positions left
        :param board: a Board representing the board to check positions on
        :return: True if there are any unchecked positions, otherwise false
        """
        return not len(super().get_checked_positions()) == board.get_height() ** 2

    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
        """
        Method to determine the next target Position according to the Riemann strategy, first the goal Position, then
        the Positions from top left to bottom right row by row
        :param original_target: a Position representing the original goal tile to be reached
        :param board: A Board to get potential target Positions from
        :return: A Position representing the next target position to check
        """
        if len(super().get_checked_positions()) == 0:
            return original_target
        for row in range(board.get_height()):
            for col in range(board.get_width()):
                potential_position = Position(row, col)
                if potential_position not in super().get_checked_positions():
                    return potential_position
        raise ValueError("Error: No Positions left to check")
