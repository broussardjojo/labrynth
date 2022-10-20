from .base_strategy import BaseStrategy
from ..Common.board import Board
from ..Common.position import Position


class Riemann(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """
    def __init__(self, goal_position: Position):
        """
        Constructor for a Riemann strategy which calls the BaseStrategy constructor and initializes the goal_position
        field
        :param goal_position: A Position representing the goal (or home depending on implementation) Tile's location
        """
        super().__init__()
        self.__goal_position = goal_position

    def possible_next_target_positions(self, board: Board) -> bool:
        """
        Method to determine if there are any unchecked positions left
        :param board: a Board representing the board to check positions on
        :return: True if there are any unchecked positions, otherwise false
        """
        return not len(super().get_checked_positions()) == len(board.get_tile_grid())**2


    def get_next_target_position(self, board: Board) -> Position:
        """
        Method to determine the next target Position according to the Riemann strategy, first the goal Position, then
        the Positions from top left to bottom right row by row
        :param board: A Board to get potential target Positions from
        :return: A Position representing the next target position to check
        """
        if len(super().get_checked_positions()) == 0:
            return self.__goal_position
        for row in range(len(board.get_tile_grid())):
            for col in range(len(board.get_tile_grid()[row])):
                potential_position = Position(row, col)
                if potential_position not in super().get_checked_positions():
                    return potential_position
        raise ValueError("Error: No Positions left to check")

