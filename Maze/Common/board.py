from typing import List, Set
from tile import Tile
from gem import Gem
from shapes import Shape, Line, Corner, TShaped, Cross
from utils import generate_gem_list
import random
from direction import Direction


class Board:
    """
    A Board is a representation of a Labrynth game board of size N by N, defaulting to 7. A Board has a grid of Tiles
    and an extra Tile.
    """
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1

    def __init__(self, dimensions: int = 7, **kwargs):
        """
        A constructor for a Board, taking in a dimension for the number of columns and rows that defaults to 7.
        It creates a tile_grid, generates the next_tile and creates an empty removed_tile
        :param dimensions: an integer representing the length and width of the board
        """
        if 'seed' in kwargs:
            random.seed(kwargs['seed'])
        gem_name_list = generate_gem_list()
        self.__dimensions = dimensions
        self.__tile_grid = []
        self.__initialize_board(gem_name_list, dimensions)
        self.__next_tile = self.__generate_unique_tile(gem_name_list)
        self.__removed_tile: Tile = None

    def __initialize_board(self, gem_name_list: List[str], dimension: int) -> None:
        """
        Creates a grid of N by N unique Tiles based on the dimensions given in the Board constructor. Tiles are
        designated to be unique if they don't share the same gems as any other tile in the grid.
        :param gem_name_list: List of strings representing all possible gem names
        :param dimension: integer representing the length and width of the board
        :return: None
        side effect: fills in the __tile_grid field with unique Tiles
        """
        for row in range(dimension):
            self.__tile_grid.append([])
            for column in range(dimension):
                unique_tile = self.__generate_unique_tile(gem_name_list)
                self.__tile_grid[row].append(unique_tile)

    def __generate_unique_tile(self, gem_name_list: List[str]) -> Tile:
        """
        Creates a unique Tile. A Tile is designated to be unique if it does not share the same gems as any other tiles
        in the grid.
        :param gem_name_list: List of strings representing all possible gem names
        :return: Tile representing a unique Tile
        """
        potential_tile = Tile(self.__get_random_shape(),
                              self.__get_random_gem(gem_name_list),
                              self.__get_random_gem(gem_name_list))
        for row in self.__tile_grid:
            for tile in row:
                if tile.same_gems_on_tiles(potential_tile.get_gems()[0], potential_tile.get_gems()[1]):
                    return self.__generate_unique_tile(gem_name_list)
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

    def slide(self, index: int, direction: Direction) -> None:
        """
        Slide the specified row or column of this Board in the given Direction.
        :param index: an int representing the row or column to slide
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: None
        :raises: ValueError if the given index is not eligible to slide
        side effect: mutates __tile_grid and mutates __removed_tile
        """
        if self.__can_slide(index):
            if direction == Direction.Up or direction == Direction.Down:
                self.__slide_col(index, direction)
            if direction == Direction.Right or direction == Direction.Left:
                self.__slide_row(index, direction)
        else:
            raise ValueError("Invalid index")

    def __can_slide(self, index: int) -> bool:
        """
        Checks if the given index is a row or column that can slide on this Board.
        :param index: an int representing a row or column on this Board
        :return: True if the index can slide, otherwise False
        """
        return not (index < 0 or index >= self.__dimensions or index % 2 != 0)

    def __slide_col(self, index: int, direction: Direction) -> None:
        """
        Slides the given column in the given direction.
        :param index: an int representing a column on this Board
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: None
        :raises: ValueError if a Direction of Right or Left is passed in
        side effect: mutates __tile_grid and __removed_tile
        """
        if direction == Direction.Up:
            self.__slide_up(index)
        elif direction == Direction.Down:
            self.__slide_down(index)
        else:
            raise ValueError("Invalid Direction")

    def __slide_up(self, index: int) -> None:
        """
        Slides the given column up.
        :param index: represents a column on this Board
        :return: None
        side effect: mutates __tile_grid and __removed_tile
        """
        self.__removed_tile = self.__tile_grid[0][index]
        for row in range(1, self.__dimensions):
            self.__tile_grid[row - 1][index] = self.__tile_grid[row][index]
            self.__tile_grid[row][index] = None

    def __slide_down(self, index: int) -> None:
        """
        Slides the given column down.
        :param index: represents a column on this Board
        :return: None
        side effect: mutates __tile_grid and __removed_tile
        """
        self.__removed_tile = self.__tile_grid[self.__dimensions - 1][index]
        for row in reversed(range(0, self.__dimensions - 1)):
            self.__tile_grid[row + 1][index] = self.__tile_grid[row][index]
            self.__tile_grid[row][index] = None

    def __slide_row(self, index: int, direction: Direction) -> None:
        """
        Slides the given row in the given direction.
        :param index: an int representing a row on this Board
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: None
        :raises: ValueError if a Direction of Up or Down is passed in
        side effect: mutates __tile_grid and __removed_tile
        """
        if direction == Direction.Right:
            self.__slide_right(index)
        elif direction == Direction.Left:
            self.__slide_left(index)
        else:
            raise ValueError("Invalid Direction")

    def __slide_right(self, index: int) -> None:
        """
        Slides the given row to the right.
        :param index: represents a row on this Board
        :return: None
        side effect: mutates __tile_grid and __removed_tile
        """
        self.__removed_tile = self.__tile_grid[index][self.__dimensions - 1]
        for col in reversed(range(0, self.__dimensions - 1)):
            self.__tile_grid[index][col + 1] = self.__tile_grid[index][col]
            self.__tile_grid[index][col] = None

    def __slide_left(self, index: int) -> None:
        """
        Slides the given row to the left.
        :param index: represents a row on this Board
        :return: None
        side effect: mutates __tile_grid and __removed_tile
        """
        self.__removed_tile = self.__tile_grid[index][0]
        for col in range(1, self.__dimensions):
            self.__tile_grid[index][col - 1] = self.__tile_grid[index][col]
            self.__tile_grid[index][col] = None

    def insert_tile(self) -> None:
        """
        Inserts a tile where there is a gap in this Board.
        :return: None
        :raises: ValueError if there are no gaps in this Board
        side effect: mutates __tile_grid and __next_tile
        """
        for row in range(len(self.__tile_grid)):
            for col in range(len(self.__tile_grid[row])):
                if self.__tile_grid[row][col] is None:
                    self.__tile_grid[row][col] = self.__next_tile
                    self.__next_tile = self.__removed_tile
                    return
        raise ValueError("No empty slots")

    def reachable_tiles(self, base_tile: Tile) -> Set[Tile]:
        """
        Given a base Tile, gets a Set of reachable Tiles on this Board
        :param base_tile: the Tile representing the start Tile for the search
        :return: a Set of all reachable Tiles not including the base Tile
        """
        all_reachable = self.__reachable_tiles_helper(base_tile)
        all_reachable.remove(base_tile)
        return all_reachable

    def __reachable_tiles_helper(self, base_tile: Tile, acc_tiles: Set[Tile] = None) -> Set[Tile]:
        """
        Given a base Tile, gets a Set of reachable Tiles on this Board
        :param base_tile: the Tile representing the start Tile for the search
        :param acc_tiles: accumulator representing the Set of all reachable Tiles
        :return: a Set of all reachable Tiles including the base Tile
        """
        if acc_tiles is None:
            acc_tiles = []
        acc_tiles.append(base_tile)
        for direction in [self.RIGHT, self.LEFT]:
            neighbor = self.__check_neighbor(base_tile, 0, direction)
            if neighbor not in acc_tiles:
                self.__reachable_tiles_helper(neighbor, acc_tiles)
        for direction in [self.UP, self.DOWN]:
            neighbor = self.__check_neighbor(base_tile, direction, 0)
            if neighbor not in acc_tiles:
                self.__reachable_tiles_helper(neighbor, acc_tiles)
        return acc_tiles

    @staticmethod
    def __connected_tile(base_tile: Tile, neighbor_tile: Tile, base_path: Direction, neighbor_path: Direction) \
            -> Tile:
        """
        Checks if the two given Tiles are connected in the given Directions
        :param base_tile: The source Tile to check the connection of
        :param neighbor_tile: The neighbor Tile to check the connection of
        :param base_path: A Direction representing the Direction to check from the base_tile
        :param neighbor_path: A Direction representing the Direction to check from the neighbor_path
        :return: A Tile, if the function finds a connected neighbor, it will return the neighbor. If it does not,
        it will return the given base Tile
        """
        if base_tile.has_path(base_path) and neighbor_tile.has_path(neighbor_path):
            return neighbor_tile
        return base_tile

    def __check_neighbor(self, base_tile, row_offset: int, col_offset: int) -> Tile:
        """
        Checks if the given Tile has a connected neighbor at the given offsets
        :param base_tile: A Tile representing the source tile to search from
        :param row_offset: An int representing the offset in the x direction between the base and neighbor tile
        :param col_offset: An int representing the offset in the y direction between the base and neighbor tile
        :return: A Tile, if the function finds a connected neighbor, it will return the neighbor. If it does not,
        it will return the given base Tile
        """
        base_row, base_col = self.__get_index_by_tile(base_tile)
        if self.__valid_tile_location(base_row + row_offset, base_col + col_offset):
            neighbor_tile = self.__tile_grid[base_row + row_offset][base_col + col_offset]
            if col_offset == self.RIGHT:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Right, Direction.Left)
            elif col_offset == self.LEFT:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Left, Direction.Right)
            elif row_offset == self.UP:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Up, Direction.Down)
            elif row_offset == self.DOWN:
                return self.__connected_tile(base_tile, neighbor_tile, Direction.Down, Direction.Up)
        else:
            return base_tile

    def __get_index_by_tile(self, base_tile: Tile) -> (int, int):
        """
        Gets the index of the given Tile
        :param base_tile: A Tile representing the target tile to search for in the board
        :return: A tuple (int, int) representing the row and column indices of the base_tile
        :raises: ValueError if the supplied Tile is not on the board
        """
        for row in range(len(self.__tile_grid)):
            for col in range(len(self.__tile_grid[row])):
                if self.__tile_grid[row][col] == base_tile:
                    return row, col
        raise ValueError("Tile not on board")

    def __valid_tile_location(self, row, col):
        """
        Checks if the given indices are within the bounds of the board
        :param row: An int representing the row of the potential Tile
        :param col: An int representing the column of the potential Tile
        :return: True if the supplied indices are within the board, False otherwise
        """
        return (0 <= row < self.__dimensions) and (0 <= col < self.__dimensions)

    def get_tile_grid(self) -> List[List[Tile]]:
        """
        Gets the tile grid for this Board
        :return: the tile grid for this Board
        """
        return self.__tile_grid

    def get_removed_tile(self) -> Tile:
        """
        Gets the extra tile for this Board
        :return: the extra tile for this Board
        """
        return self.__removed_tile

    def get_next_tile(self) -> Tile:
        """
        Gets the next tile to be inserted into this Board
        :return: the next tile for this Board
        """
        return self.__next_tile
