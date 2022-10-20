from copy import deepcopy
from typing import List

from .move import Move
from ..Common.direction import Direction
from ..Common.position import Position
from ..Common.state import ObservableState
from ..Common.tile import Tile
from .strategy import Strategy
from ..Common.board import Board
from ..Common.utils import get_opposite_direction
from abc import abstractmethod


class BaseStrategy(Strategy):
    def __init__(self):
        self.__checked_positions = []

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Move:
        """
        Generates a Move based on a BaseStrategy format: 1. pick a target destination, 2. try all moves to achieve that,
        3. if successful, do that move, if not, pick a new target and repeat
        :param current_state: an ObservableState representing the current state of the board
        :param current_position: a Position representing the original position to move from
        :param target_position: a Position representing the end goal to go to
        :return: A Move representing either a rotate, slide/insert, and move or a Pass
        """
        board_copy = deepcopy(current_state.get_board())
        base_tile = board_copy.get_tile_by_position(current_position)
        target_tile = board_copy.get_tile_by_position(target_position)
        return self.__generate_possible_move(board_copy, base_tile, target_tile)

    @abstractmethod
    def get_next_target_position(self, board: Board) -> Position:
        pass

    @abstractmethod
    def possible_next_target_positions(self, board: Board) -> bool:
        pass

    def __reset_checked_positions(self):
        self.__checked_positions = []

    def get_checked_positions(self):
        return self.__checked_positions

    def __check_possible_slides(self, board: Board, target_tile: Tile,
                                base_tile: Tile, directions: List[Direction]) -> Move:
        target_position = board.get_position_by_tile(target_tile)
        for index in range(0, len(board.get_tile_grid()), 2):
            for slide_direction in directions:
                rotations = 0
                for rotation in range(4):
                    board.get_next_tile().rotate(1)
                    board.slide_and_insert(index, slide_direction)
                    if target_tile in board.reachable_tiles(base_tile) and target_tile != base_tile:
                        self.__reset_checked_positions()
                        return Move(index, slide_direction, rotations*90, target_position, False)
                    self.__undo_slide(index, slide_direction, board)
                    rotations += 1
        return Move(-1, Direction.Up, 0, target_position, True)

    def __generate_possible_move(self, board_copy, base_tile, target_tile) -> Move:
        possible_move = self.__check_possible_slides(board_copy, target_tile, base_tile,
                                                     [Direction.Left, Direction.Right])
        if not possible_move.is_pass():
            return possible_move
        possible_move = self.__check_possible_slides(board_copy, target_tile, base_tile,
                                                     [Direction.Up, Direction.Down])
        if not possible_move.is_pass():
            return possible_move
        self.__checked_positions.append(board_copy.get_position_by_tile(target_tile))
        if self.possible_next_target_positions(board_copy):
            return self.__generate_possible_move(board_copy, base_tile,
                                                 board_copy.get_tile_by_position(
                                                     self.get_next_target_position(board_copy)))
        return possible_move

    @staticmethod
    def __undo_slide(prev_index: int, prev_direction: Direction, board: Board) -> None:
        opposite_direction = get_opposite_direction(prev_direction)
        board.slide_and_insert(prev_index, opposite_direction)
