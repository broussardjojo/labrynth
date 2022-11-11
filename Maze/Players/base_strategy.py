from abc import abstractmethod
from copy import deepcopy
from typing import List, Union, Tuple

from .move import Move, Pass
from .strategy import Strategy
from ..Common.board import Board
from ..Common.direction import Direction
from ..Common.observableState import ObservableState
from ..Common.position import Position
from ..Common.position_transition_map import PositionTransitionMap

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
        # BaseStrategy always checks all row slides, then all column slides
        return self.__check_horizontal(board_copy, current_position,
                                       target_position,
                                       original_goal=target_position,
                                       previous_moves=current_state.get_all_previous_non_passes())

    @abstractmethod
    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
        """
        Method to be implemented in classes that extend BaseStrategy, determines the next position to check
        :param original_target: a Position representing the original goal tile to be reached
        :param board: The board to get the next Position from
        :return: a Position representing the next Position to use as a goal
        """

    @abstractmethod
    def possible_next_target_positions(self, board: Board) -> bool:
        """
        Method to check if there are any possible positions left to check
        :param board: A Board which can be used to determine how many tiles we should check
        :return: True if there are more positions to check, False otherwise
        """

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

    def __check_possible_slides(self, board: Board, base_position: Position, target_position: Position,
                                previous_moves: List[Tuple[int, Direction]], directions: List[Direction]) -> Union[Move, Pass]:
        """
        A method to check all possible moves in the order sliding the specified row or column in the provided directions
        :param board: A Board to perform temporary slides on
        :param target_position: A Position representing the target Position to look for
        :param base_position: A Position representing the Position to start from
        :param directions: The Directions to slide the rows/columns in
        :return: A Move representing either a valid Move to the target or a pass if no move is found
        """
        for index in range(0, board.get_height(), 2):
            for slide_direction in directions:
                if previous_moves:
                    previous_index, previous_direction = previous_moves[-1]
                    if previous_index == index and previous_direction == slide_direction.get_opposite_direction():
                        continue
                for rotation in range(FULL_ROTATION):
                    board.get_next_tile().rotate(rotation)
                    transitions = board.slide_and_insert(index, slide_direction)
                    shifted_base_position = self.__adjust_position(transitions, base_position)
                    reachable_positions = board.reachable_tiles(shifted_base_position)
                    if target_position in reachable_positions and target_position != shifted_base_position:
                        self.__reset_checked_positions()
                        return Move(index, slide_direction, rotation * 90, target_position)
                    self.__undo_slide(index, slide_direction, board)
                    board.get_next_tile().rotate(FULL_ROTATION - rotation)
        return Pass()

    @staticmethod
    def __adjust_position(transitions: PositionTransitionMap, old_position: Position) -> Position:
        """
        Method to get an adjusted Position after the slide described by a given transition map has been made
        :param transitions: a PositionTransitionMap representing a slide and insert action that has been performed
        :param old_position: the position of the tile to adjust, before taking into account the slide/insert
        :return: The new position of the tile to adjust, or the position of the most recently inserted tile if the one
        at prev_position left the board.
        """
        if old_position in transitions.updated_positions:
            return transitions.updated_positions[old_position]
        if old_position == transitions.removed_position:
            return transitions.inserted_position
        # If the position was not updated, return the same position
        return old_position

    def __check_horizontal(self, board_copy: Board, base_position: Position, target_position: Position,
                           original_goal: Position,
                           previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move by sliding rows, then columns, loops through targets to move to in an order
        specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_position: A Tile representing the Tile to start from
        :param target_position: A Tile representing the target Tile to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if no move is found
        """
        possible_move = self.__check_possible_slides(board_copy, base_position, target_position, previous_moves,
                                                     [Direction.LEFT, Direction.RIGHT])
        return possible_move.return_if_move_perform_action_if_pass(lambda: self.__check_vertical(board_copy,
                                                                                                 base_position,
                                                                                                 target_position,
                                                                                                 original_goal,
                                                                                                 previous_moves))

    def __check_vertical(self, board_copy: Board, base_position: Position, target_position: Position,
                         original_goal: Position,
                         previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move by sliding columns, loops through targets to move to in an order
        specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_position: A Tile representing the Tile to start from
        :param target_position: A Tile representing the target Tile to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if no move is found
        """
        possible_move = self.__check_possible_slides(board_copy, base_position, target_position, previous_moves,
                                                     [Direction.UP, Direction.DOWN])
        return possible_move.return_if_move_perform_action_if_pass(lambda: self.__check_new_goal(board_copy,
                                                                                                 base_position,
                                                                                                 target_position,
                                                                                                 original_goal,
                                                                                                 previous_moves))

    def __check_new_goal(self, board_copy: Board, base_position: Position, target_position: Position,
                         original_goal: Position, previous_moves: List[Tuple[int, Direction]]) -> Union[Move, Pass]:
        """
        Checks if there is a possible move for the next target to move to in an order specified in implementations
        :param board_copy: A Board to perform temporary slides on
        :param base_position: A Position representing the Position to start from
        :param target_position: A Position representing the target Position to look for
        :param original_goal: A Position representing the original goal Position to look for
        :return: A Move representing either a valid Move to a target or a Pass if there are no more targets
        """
        self.__checked_positions.append(target_position)
        if self.possible_next_target_positions(board_copy):
            return self.__check_horizontal(board_copy, base_position,
                                           self.get_next_target_position(board_copy, original_goal),
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
        board.slide_and_insert(prev_index, prev_direction.get_opposite_direction())
