from typing import List, Iterator

from Maze.Common.abstract_state import AbstractState
from Maze.Common.position import Position
from Maze.Common.utils import get_euclidean_distance_between
from Maze.Players.base_strategy import BaseStrategy


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
