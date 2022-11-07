from copy import deepcopy
from typing import List, Set, Union, Tuple

from .move import Move, Pass
from ..Common.direction import Direction
from ..Common.position import Position
from ..Common.observableState import ObservableState
from ..Common.tile import Tile
from .strategy import Strategy
from ..Common.board import Board
from ..Common.utils import get_opposite_direction
from abc import abstractmethod

FULL_ROTATION = 4


class BaseStrategy(Strategy):
    """
    A BaseStrategy representing a general type of strategy which picks a target and tries every possible slide/insert
    and rotate to see if it's possible to reach it, then gets a new target and repeats, passing if there are no
    more targets to try.
    """

    def __init__(self):
        """
        Constructor for a BaseStrategy which initializes the __checked_positions list to an empty list because no
        positions have been checked yet.
        """
        self.__checked_positions = []

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Union[Move, Pass]:
        """
        Generates a Move based on a BaseStrategy format: 1. pick a target destination, 2. try all moves to achieve that,
        3. if successful, do that move, if not, pick a new target and repeat
        :param current_state: an ObservableState representing the current state of the board
        NOTE: an ObservableState provides access to a reference to the a Board so it is important to make a deep copy
        to prevent unwanted mutations.
        :param current_position: a Position representing the original position to move from
        :param target_position: a Position representing the end goal to go to
        :return: A Move representing either a rotate, slide/insert, and move or a Pass
        """
        board_copy = deepcopy(current_state.get_board())
        base_tile = board_copy.get_tile_by_position(current_position)
        target_tile = board_copy.get_tile_by_position(target_position)
        return self.__generate_possible_move(board_copy, base_tile,
                                             target_tile, target_position,
                                             current_state.get_all_previous_non_passes())

    @abstractmethod
    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
        """
        Method to be implemented in classes that extend BaseStrategy, determines the next position to check
        :param original_target: a Position representing the original goal tile to be reached
        :param board: The board to get the next Position from
        :return: a Position representing the next Position to use as a goal
        """
        pass

    @abstractmethod
    def possible_next_target_positions(self, board: Board) -> bool:
        """
        Method to check if there are any possible positions left to check
        :param board: A Board which can be used to determine how many tiles we should check
        :return: True if there are more positions to check, False otherwise
        """
        pass

    def __reset_checked_positions(self) -> None:
        """
        Method to clear the list of checked positions so the next move can be determined from scratch
        :return: None
        """
        self.__checked_positions = []

    def get_checked_positions(self) -> List[Position]:
        """
        Getter for the __checked_positions attribute
        :return: A List of Positions representing all positions that have been checked in this run of the Strategy
        """
        return self.__checked_positions

    def __check_possible_slides(self, board: Board, target_tile: Tile,
                                base_tile: Tile, previous_moves: List[Tuple[int, Direction]],
                                directions: List[Direction]) -> Union[Move, Pass]:
        """
        A method to check all possible moves in the order sliding the specified row or column in the provided directions
        :param board: A Board to perform temporary slides on
        :param target_tile: A Tile representing the target Tile to look for
        :param base_tile: A Tile representing the Tile to start from
        :param directions: The Directions to slide the rows/columns in
        :return: A Move representing either a valid Move to the target or a pass if no move is found
        """
        target_position = board.get_position_by_tile(target_tile)
        for index in range(0, len(board.get_tile_grid()), 2):
            for slide_direction in directions:
                if previous_moves:
                    previous_index, previous_direction = previous_moves[-1]
                    if previous_index == index and previous_direction == get_opposite_direction(slide_direction):
                        continue
                for rotation in range(FULL_ROTATION):
                    board.get_next_tile().rotate(rotation)
                    adjusted_base_tile = self.__adjust_base_tile_on_edge(board, base_tile,
                                                                         index, slide_direction)
                    transitions = board.slide_and_insert(index, slide_direction)
                    reachable_positions = \
                        self.__get_reachable_positions_from_tile(board, board.reachable_tiles(adjusted_base_tile))
                    slid_target_tile = board.get_tile_by_position(target_position)
                    if target_position in reachable_positions and slid_target_tile != adjusted_base_tile:
                        self.__reset_checked_positions()
                        return Move(index, slide_direction, rotation * 90, target_position)
                    self.__undo_slide(index, slide_direction, board)
                    board.get_next_tile().rotate(FULL_ROTATION - rotation)
        return Pass()

    @staticmethod
    def __adjust_base_tile_on_edge(board: Board, base_tile: Tile, index: int, slide_direction: Direction) -> Tile:
        """
        Method to get an adjusted Tile based on a slide action
        :param board: a Board representing the Board this slide was performed on
        :param base_tile: a Tile representing the Tile in the starting location
        :param index: an int representing the row/col of the slide
        :param slide_direction: a Direction representing the direction of the slide
        :return: A Tile representing either the base_tile if the base_tile was not slid off or the next_tile if the
        base_tile was slid off.
        """
        base_tile_position = board.get_position_by_tile(base_tile)
        if (slide_direction == Direction.Up and base_tile_position.get_row() == 0
                and index == base_tile_position.get_col()):
            return board.get_next_tile()
        if (slide_direction == Direction.Down and base_tile_position.get_row() == len(board.get_tile_grid()) - 1
                and index == base_tile_position.get_col()):
            return board.get_next_tile()
        if (slide_direction == Direction.Left and base_tile_position.get_col() == 0
                and index == base_tile_position.get_row()):
            return board.get_next_tile()
        if (slide_direction == Direction.Right and base_tile_position.get_col() == len(board.get_tile_grid()) - 1
                and index == base_tile_position.get_row()):
            return board.get_next_tile()
        return base_tile

    def __generate_possible_move(self, board_copy: Board, base_tile: Tile, target_tile: Tile,
                                 original_goal: Position,
                                 previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move by sliding rows, then columns, loops through targets to move to in an order
        specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_tile: A Tile representing the Tile to start from
        :param target_tile: A Tile representing the target Tile to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if no move is found
        """
        possible_move = self.__check_possible_slides(board_copy, target_tile, base_tile, previous_moves,
                                                     [Direction.Left, Direction.Right])
        return possible_move.return_if_move_perform_action_if_pass(lambda: self.__check_vertical(board_copy,
                                                                                                 target_tile,
                                                                                                 base_tile,
                                                                                                 original_goal,
                                                                                                 previous_moves))

    def __check_vertical(self, board_copy, target_tile, base_tile, original_goal,
                         previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move by sliding columns, loops through targets to move to in an order
        specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_tile: A Tile representing the Tile to start from
        :param target_tile: A Tile representing the target Tile to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if no move is found
        """
        possible_move = self.__check_possible_slides(board_copy, target_tile, base_tile, previous_moves,
                                                     [Direction.Up, Direction.Down])
        return possible_move.return_if_move_perform_action_if_pass(lambda: self.__check_new_goal(board_copy,
                                                                                                 target_tile,
                                                                                                 base_tile,
                                                                                                 original_goal,
                                                                                                 previous_moves))

    def __check_new_goal(self, board_copy: Board, target_tile: Tile, base_tile: Tile, original_goal: Position,
                         previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move for the next target to move to in an order specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_tile: A Tile representing the Tile to start from
        :param target_tile: A Tile representing the target Tile to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if there are no more targets
        """
        self.__checked_positions.append(board_copy.get_position_by_tile(target_tile))
        if self.possible_next_target_positions(board_copy):
            return self.__generate_possible_move(board_copy, base_tile,
                                                 board_copy.get_tile_by_position(
                                                     self.get_next_target_position(board_copy, original_goal)),
                                                 original_goal, previous_moves)
        self.__reset_checked_positions()
        return Pass()

    @staticmethod
    def __undo_slide(prev_index: int, prev_direction: Direction, board: Board) -> None:
        """
        A method to reverse a slide on a given board given an index and direction of the previous move
        :param prev_index: an int representing the previous index (row or column) that was slid on
        :param prev_direction: a Direction representing the direction the previous slide was made in
        :param board: A Board to perform temporary slides on
        :return: None
        """
        opposite_direction = get_opposite_direction(prev_direction)
        board.slide_and_insert(prev_index, opposite_direction)

    @staticmethod
    def __get_reachable_positions_from_tile(board: Board, reachable_tiles: Set[Tile]) -> List[Position]:
        """
        Gets the list of reachable Positions on a Board from the Set of reachable Tiles
        :param board: a Board representing the board to find the Positions on
        :param reachable_tiles: a Set of Tiles representing all the reachable Tiles on a Board from a given starting
        Tile
        :return: A List of Positions representing all the reachable Positions on this Board from a given starting
        Position
        """
        return list(map(board.get_position_by_tile, reachable_tiles))
