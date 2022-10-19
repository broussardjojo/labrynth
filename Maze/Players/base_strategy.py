from copy import deepcopy

from .move import ValidMove, PassMove, Move
from ..Common.direction import Direction
from ..Common.position import Position
from ..Common.state import ObservableState
from .strategy import Strategy
from ..Common.board import Board
from abc import abstractmethod, ABC


class BaseStrategy(Strategy, ABC):
    def __init__(self):
        self.__checked_positions = []

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        board_copy = deepcopy(current_state.get_board())
        base_tile = board_copy.get_tile_by_position(current_position)
        target_tile = board_copy.get_tile_by_position(target_position)
        return self.__generate_possible_move(board_copy, base_tile, target_tile)


    @abstractmethod
    def get_next_target_position(self):
        pass

    @abstractmethod
    def possible_next_target_positions(self):
        pass

    def reset_checked_positions(self):
        self.__checked_positions = []

    def get_checked_positions(self):
        return self.__checked_positions

    def __generate_possible_move(self, board_copy, base_tile, target_tile):
        target_position = board_copy.get_position_by_tile(target_tile)
        for index in range(0, len(board_copy.get_tile_grid())):
            for slide_direction in Direction:
                rotations = 0
                for rotation in range(4):
                    rotations += 1
                    board_copy.get_next_tile().rotate(1)
                    board_copy.slide_and_insert(index, slide_direction)
                    if target_tile in board_copy.reachable_tiles(base_tile):
                        self.reset_checked_positions()
                        return ValidMove(index, slide_direction, rotations, target_position)
                    self.__undo_slide(index, slide_direction, board_copy)
        if self.possible_next_target_positions():
            return self.generate_move(board_copy, base_tile, self.get_next_target_position())
        return PassMove()

    def __undo_slide(self, prev_index: int, prev_direction: Direction, board: Board) -> None:
        pass
