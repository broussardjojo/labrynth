from .base_strategy import BaseStrategy
from ..Common.board import Board
from ..Common.position import Position


class Euclid(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """
    def __init__(self, goal_position: Position):
        """
        Constructor for a Euclid strategy which calls the BaseStrategy constructor and initializes the goal_position
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
        return not len(super().get_checked_positions()) == len(board.get_tile_grid()) ** 2

    @staticmethod
    def __get_euclidean_distance_between(position_one: Position, position_two: Position) -> int:
        """
        Determines the Euclidean distance between two Positions using the distance formula: (x1-x2)^2 + (y1-y2)^2
        NOTE: While the distance formula does take the square root of the result at the end, we chose not to do this
        as we are comparing which is larger and not by how much in the only use of this function, taking the square
        root would lead to either casting results to ints (inaccurate) or having to use floats (prone to error)
        :param position_one: The first Position (p1)
        :param position_two: The second Position (p2)
        :return: An int representing the euclidean distance between two given positions
        """
        return (position_one.get_row() - position_two.get_row()) ** 2 + \
               (position_one.get_col() - position_two.get_col()) ** 2

    def get_next_target_position(self, board: Board) -> Position:
        """
        Method to determine the next target Position according to the Euclid strategy, first the goal Position, then
        the Positions from top left to bottom right row by row
        :param board: A Board to get potential target Positions from
        :return: A Position representing the next target position to check
        :raises: ValueError if there are no Positions left to check
        """
        if len(super().get_checked_positions()) == 0:
            return self.__goal_position
        first_unchecked_position = self.__get_first_unchecked(board)
        min_distance = self.__get_euclidean_distance_between(first_unchecked_position, self.__goal_position)
        min_position = first_unchecked_position
        for row in range(len(board.get_tile_grid())):
            for col in range(len(board.get_tile_grid()[row])):
                potential_position = Position(row, col)
                euclidean_distance = self.__get_euclidean_distance_between(potential_position, self.__goal_position)
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
        for row in range(len(board.get_tile_grid())):
            for col in range(len(board.get_tile_grid()[row])):
                if Position(row, col) not in super().get_checked_positions():
                    return Position(row, col)
        raise ValueError("Error: No Positions left to check")
