from typing import List, Set
from tile import Tile
from gem import Gem
from shapes import Shape, Line, Corner, TShaped, Cross
from utils import generate_gem_list
import random
from direction import Direction
from position import Position


class Board:
    """
    A Board is a representation of a Labyrinth game board of size N by N, defaulting to 7. A Board has a grid of Tiles
    and an extra Tile. The grid is 0-indexed, row majored, and board[0][0] represents the Tile at the top-left.
    spot on this Board.
    """
    UP_OFFSET = -1
    DOWN_OFFSET = 1
    LEFT_OFFSET = -1
    RIGHT_OFFSET = 1

    def __init__(self, tile_grid: List[List[Tile]], next_tile: Tile):
        self.__tile_grid = tile_grid
        self.__next_tile = next_tile
        self.__dimensions = len(tile_grid)

    @classmethod
    def from_list_of_tiles(cls, tile_grid: List[List[Tile]]):
        gem_name_list = generate_gem_list()
        next_tile = cls.__generate_unique_tile(gem_name_list, tile_grid)
        return cls(tile_grid, next_tile)

    @classmethod
    def from_random_board(cls, dimensions: int = 7, **kwargs):
        """
        A constructor for a Board, taking in a dimension for the number of columns and rows that defaults to 7.
        It creates a tile_grid and generates the next_tile.
        :param dimensions: an integer representing the length and width of the board
        """
        if 'seed' in kwargs:
            random.seed(kwargs['seed'])
        gem_name_list = generate_gem_list()
        board = cls.__initialize_board(gem_name_list, dimensions)
        next_tile = cls.__generate_unique_tile(gem_name_list, board)
        return cls(board, next_tile)

    @classmethod
    def __initialize_board(cls, gem_name_list: List[str], dimension: int) -> List[List[Tile]]:
        """
        Creates a grid of N by N unique Tiles based on the dimensions given in the Board constructor. Tiles are
        designated to be unique if they don't share the same two gems as any other tile in the grid.
        :param gem_name_list: List of strings representing all possible gem names
        :param dimension: integer representing the length and width of the board
        :return: None
        side effect: fills in the __tile_grid field with unique Tiles
        """
        board = []
        for row in range(dimension):
            board.append([])
            for column in range(dimension):
                unique_tile = cls.__generate_unique_tile(gem_name_list, board)
                board[row].append(unique_tile)
        return board

    @classmethod
    def __generate_unique_tile(cls, gem_name_list: List[str], current_board: List[List[Tile]]) -> Tile:
        """
        Creates a unique Tile. A Tile is designated to be unique if it does not share the same two gems as any other
        tiles in the grid.
        :param gem_name_list: List of strings representing all possible gem names
        :return: Tile representing a unique Tile
        """
        potential_tile = Tile(cls.__get_random_shape(),
                              cls.__get_random_gem(gem_name_list),
                              cls.__get_random_gem(gem_name_list))
        for row in current_board:
            for tile in row:
                if tile.same_gems_on_tiles(potential_tile.get_gems()[0], potential_tile.get_gems()[1]):
                    return cls.__generate_unique_tile(gem_name_list, current_board)
        return potential_tile

    @staticmethod
    def __get_random_shape() -> Shape:
        """
        Generates a random Shape.
        :return: a Shape, which is one of: Line, Corner, TShaped, Cross
        """
        all_shape_dict = {
            0: Line(0),
            1: Corner(0),
            2: TShaped(0),
            3: Cross()
        }
        random_shape = all_shape_dict[random.randint(0, len(all_shape_dict) - 1)]
        return random_shape

    @staticmethod
    def __get_random_gem(gem_name_list: List[str]) -> Gem:
        """
        Generates a random Gem based on the list of given gem names.
        :param gem_name_list: list of all possible gem names
        :return: a Gem, which is one of the Gems provided in the given list of gem names
        """
        return Gem(gem_name_list[random.randint(0, len(gem_name_list) - 1)])

    def slide_and_insert(self, index: int, direction: Direction) -> None:
        """
        Slides the row or column at the given index of this Board in the given Direction and inserts this Board's
        __next_tile at the end of that row or column.
        :param index: an int representing the row or column to slide
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: None
        :raises: ValueError if the given index is not eligible to slide
        side effect: mutates __tile_grid and mutates __next_tile
        """
        if self.__can_slide(index):
            if direction == Direction.Up:
                self.__slide_up(index)
            elif direction == Direction.Down:
                self.__slide_down(index)
            elif direction == Direction.Right:
                self.__slide_right(index)
            elif direction == Direction.Left:
                self.__slide_left(index)
        else:
            raise ValueError("Invalid index")

    def __can_slide(self, index: int) -> bool:
        """
        Checks if the given index is on this Board.
        :param index: an int representing a row or column on this Board
        :return: True if the index can slide, otherwise False
        """
        return not (index < 0 or index >= self.__dimensions or index % 2 != 0)

    def __slide_up(self, index: int) -> None:
        """
        Slides the given column up.
        :param index: represents a column on this Board
        :return: None
        side effect: mutates __tile_grid and __next_tile
        """
        removed_tile = self.__tile_grid[0][index]
        for row in range(1, self.__dimensions):
            self.__tile_grid[row - 1][index] = self.__tile_grid[row][index]
            self.__tile_grid[row][index] = self.__next_tile
        self.__next_tile = removed_tile

    def __slide_down(self, index: int) -> None:
        """
        Slides the given column down.
        :param index: represents a column on this Board
        :return: None
        side effect: mutates __tile_grid and __next_tile
        """
        removed_tile = self.__tile_grid[self.__dimensions - 1][index]
        for row in reversed(range(0, self.__dimensions - 1)):
            self.__tile_grid[row + 1][index] = self.__tile_grid[row][index]
            self.__tile_grid[row][index] = self.__next_tile
        self.__next_tile = removed_tile

    def __slide_right(self, index: int) -> None:
        """
        Slides the given row to the right.
        :param index: represents a row on this Board
        :return: None
        side effect: mutates __tile_grid and __next_tile
        """
        removed_tile = self.__tile_grid[index][self.__dimensions - 1]
        for col in reversed(range(0, self.__dimensions - 1)):
            self.__tile_grid[index][col + 1] = self.__tile_grid[index][col]
            self.__tile_grid[index][col] = self.__next_tile
        self.__next_tile = removed_tile

    def __slide_left(self, index: int) -> None:
        """
        Slides the given row to the left.
        :param index: represents a row on this Board
        :return: None
        side effect: mutates __tile_grid and __next_tile
        """
        removed_tile = self.__tile_grid[index][0]
        for col in range(1, self.__dimensions):
            self.__tile_grid[index][col - 1] = self.__tile_grid[index][col]
            self.__tile_grid[index][col] = self.__next_tile
        self.__next_tile = removed_tile

    def reachable_tiles(self, base_tile: Tile) -> Set[Tile]:
        """
        Given a base Tile, gets a Set of reachable Tiles on this Board
        :param base_tile: the Tile representing the start Tile for the search
        :return: a Set of all reachable Tiles
        """
        all_reachable = self.__reachable_tiles_helper(base_tile, set())
        return all_reachable

    def __reachable_tiles_helper(self, base_tile: Tile, acc_tiles) -> Set[Tile]:
        """
        Given a base Tile, gets a Set of reachable Tiles on this Board
        :param base_tile: the Tile representing the start Tile for the search
        :param acc_tiles: accumulator representing the Set of all reachable Tiles
        :return: a Set of all reachable Tiles including the base Tile
        """
        acc_tiles.add(base_tile)
        for direction_offset in [self.RIGHT_OFFSET, self.LEFT_OFFSET]:
            neighbor = self.__check_neighbor(base_tile, 0, direction_offset)
            if neighbor not in acc_tiles:
                self.__reachable_tiles_helper(neighbor, acc_tiles)
        for direction_offset in [self.UP_OFFSET, self.DOWN_OFFSET]:
            neighbor = self.__check_neighbor(base_tile, direction_offset, 0)
            if neighbor not in acc_tiles:
                self.__reachable_tiles_helper(neighbor, acc_tiles)
        return acc_tiles

    def __connected_tile(self, base_tile: Tile, neighbor_tile: Tile, base_path: Direction) -> Tile:
        """
        Checks if the two given Tiles are connected by the given Direction on the base Tile
        :param base_tile: The source Tile to check the connection of
        :param neighbor_tile: The neighbor Tile to check the connection of
        :param base_path: A Direction representing the Direction to check from the base_tile
        :return: A Tile, if the function finds a connected neighbor, it will return the neighbor. If it does not,
        it will return the given base Tile
        """
        neighbor_path = self.__get_opposite_path(base_path)
        if base_tile.has_path(base_path) and neighbor_tile.has_path(neighbor_path):
            return neighbor_tile
        return base_tile

    @staticmethod
    def __get_opposite_path(base_path):
        """
        Gives the opposite Direction to that of the given Direction.
        :param base_path: the Direction who's opposite is being given
        :return: a Direction, representing the opposite Direction to that of the given Direction
        """
        if base_path == Direction.Up:
            return Direction.Down
        elif base_path == Direction.Down:
            return Direction.Up
        elif base_path == Direction.Right:
            return Direction.Left
        return Direction.Right

    def __check_neighbor(self, base_tile, row_offset: int, col_offset: int) -> Tile:
        """
        Checks if the given Tile has a connected neighbor at the given offsets
        :param base_tile: A Tile representing the source tile to search from
        :param row_offset: An int representing the offset in the x direction between the base and neighbor tile
        :param col_offset: An int representing the offset in the y direction between the base and neighbor tile
        :return: A Tile, if the function finds a connected neighbor, it will return the neighbor. If it does not,
        it will return the given base Tile
        """
        base_position = self.get_position_by_tile(base_tile)
        base_row = base_position.get_row()
        base_col = base_position.get_col()
        if self.__valid_tile_location(base_row + row_offset, base_col + col_offset):
            neighbor_tile = self.__tile_grid[base_row + row_offset][base_col + col_offset]
            if col_offset == self.RIGHT_OFFSET:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Right)
            elif col_offset == self.LEFT_OFFSET:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Left)
            elif row_offset == self.UP_OFFSET:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Up)
            elif row_offset == self.DOWN_OFFSET:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Down)
        else:
            return base_tile

    def get_position_by_tile(self, base_tile: Tile) -> Position:
        """
        Gets the index of the given Tile
        :param base_tile: A Tile representing the target tile to search for in the board
        :return: A Position representing the row and column indices of the base_tile
        :raises: ValueError if the supplied Tile is not on the board
        """
        for row in range(len(self.__tile_grid)):
            for col in range(len(self.__tile_grid[row])):
                if self.__tile_grid[row][col] == base_tile:
                    return Position(row, col)
        raise ValueError("Tile not on board")

    def get_tile_by_position(self, position: Position) -> Tile:
        """
        Gets the Tile at a given position
        :param position: A Position representing the target location to search for in the board
        :return: A Tile representing the tile at the given Position
        :raises: ValueError if the supplied Position is not on the board
        """
        row = position.get_row()
        col = position.get_col()
        if self.__valid_tile_location(row, col):
            return self.__tile_grid[row][col]
        raise ValueError("Position not on board")

    def __valid_tile_location(self, row, col):
        """
        Checks if the given indices are within the bounds of the board
        :param row: An int representing the row of the potential Tile
        :param col: An int representing the column of the potential Tile
        :return: True if the supplied indices are within the board, False otherwise
        """
        return (0 <= row < self.__dimensions) and (0 <= col < self.__dimensions)

    def check_stationary_position(self, row: int, col: int) -> bool:
        """
        Checks if the given row and column are in a position on this Board that does not slide.
        :param row: the row index on this Board
        :param col: the column index on this Board
        :return: True if the row, column pair are at a stationary point in this Board, otherwise False
        """
        return row % 2 == 1 and col % 2 == 1 and self.__valid_tile_location(row, col)

    def get_all_stationary_tiles(self) -> List[Tile]:
        """
        Generates a list of all the stationary Tiles on this Board.
        :return: a List of Tiles that do not move
        """
        all_tiles = self.__tile_grid
        stationary_tiles = []
        for row in range(len(all_tiles)):
            for col in range(len(all_tiles[row])):
                if self.check_stationary_position(row, col):
                    stationary_tiles.append(all_tiles[row][col])
        return stationary_tiles

    def get_tile_grid(self) -> List[List[Tile]]:
        """
        Gets the tile grid for this Board
        :return: the tile grid for this Board
        """
        return self.__tile_grid

    def get_next_tile(self) -> Tile:
        """
        Gets the next tile to be inserted into this Board
        :return: the next tile for this Board
        """
        return self.__next_tile
