from .base_strategy import BaseStrategy
from ..Common.board import Board
from ..Common.position import Position


class Riemann(BaseStrategy):
    def __init__(self, goal_position: Position):
        super().__init__()
        self.__goal_position = goal_position

    def possible_next_target_positions(self, board: Board) -> bool:
        return not len(super().get_checked_positions()) == len(board.get_tile_grid())**2

    def get_next_target_position(self, board: Board) -> Position:
        if len(super().get_checked_positions()) == 0:
            return self.__goal_position
        for row in range(len(board.get_tile_grid())):
            for col in range(len(board.get_tile_grid()[row])):
                potential_position = Position(row, col)
                if potential_position not in super().get_checked_positions():
                    return potential_position
        raise ValueError("Error: No Positions left to check")

