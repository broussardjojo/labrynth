from typing import List, Set, Any, Optional, Callable, Tuple
from Maze.Common.tile import Tile
from Maze.Common.gem import Gem
from Maze.Common.shapes import Shape, Line, Corner, TShaped, Cross
from Maze.Common.utils import generate_gem_list
import random
from Maze.Common.direction import Direction, RIGHT_OFFSET, LEFT_OFFSET, DOWN_OFFSET, UP_OFFSET
from Maze.Common.position import Position
from Maze.Common.position_transition_map import PositionTransitionMap


class Board:
    """
    A Board is a representation of a Labyrinth game board of size N by N, defaulting to 7. A Board has a grid of Tiles
    and an extra Tile. The grid is 0-indexed, row majored, and board[0][0] represents the Tile at the top-left.
    spot on this Board.
    """

    __tile_grid: List[List[Tile]]
    __next_tile: Tile
    __height: int
    __width: int

    def __init__(self, tile_grid: List[List[Tile]], next_tile: Tile):
        """
        Base constructor for a Board that assigns the Board a 2-D List of Tiles to represent the tile grid and a Tile
        which represents the next Tile for the Board.
        :param tile_grid: a 2-D List of Tiles that represents the grid of tiles on a Board
        :param next_tile: a Tile that represents the next Tile to be inserted on a Board
        """
        if len(tile_grid) < 2 or len(tile_grid[0]) < 2:
            raise ValueError("Error: Board must be at least of size 2x2")
        self.__tile_grid = tile_grid
        self.__next_tile = next_tile
        self.__height = len(tile_grid)
        self.__width = len(tile_grid[0])
        for tile_row in tile_grid[1:]:
            if len(tile_row) != self.__width:
                raise ValueError("Error: Board must be rectangular")

    @classmethod
    def from_list_of_shapes(cls, shape_grid: List[List[Shape]], next_tile_shape: Shape,
                            treasure_provider: Optional[Callable[[int, int], Tuple[Gem, Gem]]] = None) -> "Board":
        """
        A constructor for a Board, taking in a 2-D List of TileShapes used to create a tile_grid, and one tile shape
        for the next_tile. If
        :param shape_grid: a 2-D list of tile shapes that represents the grid of tiles on a Board
        :param next_tile_shape: a TileShape representing the shape of the next tile
        :param treasure_provider: an optional (row, col) -> (Gem, Gem) function to select treasures. If not provided,
        every tile will get ("emerald", "emerald"); the next tile is represented by -1, -1
        :return: an instance of a Board
        """
        real_treasure_provider = (
            treasure_provider
            if treasure_provider is not None
            else lambda _row, _col: (Gem("emerald"), Gem("emerald"))
        )
        tile_grid: List[List[Tile]] = []
        for row, shapes in enumerate(shape_grid):
            tile_row: List[Tile] = []
            for col, shape in enumerate(shapes):
                gem1, gem2 = real_treasure_provider(row, col)
                tile = Tile(shape, gem1, gem2)
                tile_row.append(tile)
            tile_grid.append(tile_row)
        next_gem1, next_gem2 = real_treasure_provider(-1, -1)
        next_tile = Tile(next_tile_shape, next_gem1, next_gem2)
        return cls(tile_grid, next_tile)

    @classmethod
    def from_list_of_tiles(cls, tile_grid: List[List[Tile]], **kwargs) -> "Board":
        """
        A constructor for a Board, taking in a 2-D List of Tiles used to create a tile_grid and generates the next_tile.
        :param tile_grid: a 2-D list of tiles that represents the grid of tiles on a Board
        :return: an instance of a Board
        """
        gem_name_list = generate_gem_list()
        if 'seed' in kwargs:
            random.seed(kwargs['seed'])
        next_tile = cls.__generate_unique_tile(gem_name_list, tile_grid)
        return cls(tile_grid, next_tile)

    @classmethod
    def from_random_board(cls, height: int = 7, width: int = 7, **kwargs) -> "Board":
        """
        A constructor for a Board, taking in a dimension for the number of columns and rows that defaults to 7.
        It creates a tile_grid and generates the next_tile.
        :param width:
        :param height: an integer representing the length and width of the board
        :return: an instance of a Board
        """
        if 'seed' in kwargs:
            random.seed(kwargs['seed'])
        gem_name_list = generate_gem_list()
        board = cls.__initialize_board(gem_name_list, height, width)
        next_tile = cls.__generate_unique_tile(gem_name_list, board)
        return cls(board, next_tile)

    @classmethod
    def __initialize_board(cls, gem_name_list: List[str], height: int, width: int) -> List[List[Tile]]:
        """
        Creates a grid of N by N unique Tiles based on the dimensions given in the Board constructor. Tiles are
        designated to be unique if they don't share the same two gems as any other tile in the grid.
        :param gem_name_list: List of strings representing all possible gem names
        :param height: integer representing the height of the board
        :param width: integer representing the width of the board
        :return: None
        side effect: fills in the __tile_grid field with unique Tiles
        """
        board: List[List[Tile]] = []
        for _ in range(height):
            tile_row: List[Tile] = []
            for _ in range(width):
                unique_tile = cls.__generate_unique_tile(gem_name_list, board)
                tile_row.append(unique_tile)
            board.append(tile_row)
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

    def get_width(self) -> int:
        """
        Returns the width of this board.
        :return: An int specifying the number of tiles in each row of the board.
        """
        return self.__width

    def get_height(self) -> int:
        """
        Returns the height of this board.
        :return: An int specifying the number of rows in the board.
        """
        return self.__height

    def slide_and_insert(self, index: int, direction: Direction) -> PositionTransitionMap:
        """
        Slides the row or column at the given index of this Board in the given Direction and inserts this Board's
        __next_tile at the end of that row or column.
        :param index: an int representing the row or column to slide
        :param direction: a Direction representing the direction to slide the row or column, can be one of Up, Down,
        Left, or Right
        :return: a PositionTransitionMap representing the mapping of previous positions to new positions
        :raises: ValueError if the given index is not eligible to slide
        side effect: mutates __tile_grid and mutates __next_tile
        """
        if direction is Direction.UP or direction is Direction.DOWN:
            if not self.can_slide_vertically(index):
                raise ValueError("Invalid index")
            position_transitions = self.__get_slide_column_transitions(index, direction)
        else:
            if not self.can_slide_horizontally(index):
                raise ValueError("Invalid index")
            position_transitions = self.__get_slide_row_transitions(index, direction)
        self.__perform_slide_and_insert(position_transitions)
        return position_transitions

    def can_slide_horizontally(self, index: int) -> bool:
        """
        Checks if the given row index is on this Board and is slideable.
        :param index: an int representing a row on this Board
        :return: True if the row index can slide, otherwise False
        """
        return not (index < 0 or index >= self.__height or index % 2 != 0)

    def can_slide_vertically(self, index: int) -> bool:
        """
        Checks if the given column index is on this Board and is slideable.
        :param index: an int representing a column on this Board
        :return: True if the column index can slide, otherwise False
        """
        return not (index < 0 or index >= self.__width or index % 2 != 0)

    def check_stationary_position(self, row: int, col: int) -> bool:
        """
        Checks if the given row and column are in a position on this Board that does not slide.
        :param row: the row index on this Board
        :param col: the column index on this Board
        :return: True if the row, column pair are at a stationary point in this Board, otherwise False
        """
        return self.__valid_tile_location(row, col) and not (self.can_slide_vertically(row)
                                                             or self.can_slide_vertically(col))

    def __get_slide_row_transitions(self, index: int, direction: Direction) -> PositionTransitionMap:
        """
        Gets the PositionTransitionMap for a given slide index and Direction
        :param index: an int representing the index of the row to slide
        :param direction: a Direction which is one of Direction.Left or Direction.Right
        :return: a PositionTransitionMap with the appropriate slide, insert, and removal information
        """
        col_offset = LEFT_OFFSET if direction is Direction.LEFT else RIGHT_OFFSET
        last_col = self.__width - 1
        updated_positions = {
            Position(index, col): Position(index, col + col_offset)
            for col in range(self.__width)
            if 0 <= col + col_offset < self.__width
        }
        removed_position = Position(index, 0) if direction is Direction.LEFT else Position(index, last_col)
        inserted_position = Position(index, 0) if direction is Direction.RIGHT else Position(index, last_col)
        return PositionTransitionMap(updated_positions, removed_position, inserted_position)

    def __get_slide_column_transitions(self, index: int, direction: Direction) -> PositionTransitionMap:
        """
        Gets the PositionTransitionMap for a given slide index and Direction
        :param index: an int representing the index of the column to slide
        :param direction: a Direction which is one of Direction.Up or Direction.Down
        :return: a PositionTransitionMap with the appropriate slide, insert, and removal information
        """
        row_offset = UP_OFFSET if direction is Direction.UP else DOWN_OFFSET
        last_row = self.__height - 1
        updated_positions = {
            Position(row, index): Position(row + row_offset, index)
            for row in range(self.__height)
            if 0 <= row + row_offset < self.__height
        }
        removed_position = Position(0, index) if direction is Direction.UP else Position(last_row, index)
        inserted_position = Position(0, index) if direction is Direction.DOWN else Position(last_row, index)
        return PositionTransitionMap(updated_positions, removed_position, inserted_position)

    def __perform_slide_and_insert(self, transitions: PositionTransitionMap) -> None:
        """
        Slides the current grid based on the given PositionTransitionMap, sets the hole generated to the spare Tile
        and assigns the removed Tile to be the next spare Tile
        :param transitions: a PositionTransitionMap representing the movements of the slide action generated by the
        __get_slide_column_transitions and __get_slide_row_transitions helper methods
        :return: None
        """
        updates = transitions.updated_positions
        rem_row, rem_col = transitions.removed_position.get_position_tuple()
        removed_tile = self.__tile_grid[rem_row][rem_col]
        ins_row, ins_col = transitions.inserted_position.get_position_tuple()
        moved_tiles = [self.__tile_grid[row][col] for row, col in
                       map(Position.get_position_tuple, updates.keys())]
        for tile, new_pos in zip(moved_tiles, updates.values()):
            self.__tile_grid[new_pos.get_row()][new_pos.get_col()] = tile
        self.__tile_grid[ins_row][ins_col] = self.__next_tile
        self.__next_tile = removed_tile

    def reachable_tiles(self, base_position: Position) -> Set[Position]:
        """
        Given a base Position, gets a Set of reachable Positions on this Board
        :param base_position: the Position representing the start Position for the search
        :return: a Set of all reachable Positions
        """
        all_reachable = self.__reachable_tiles_helper(base_position)
        return all_reachable

    def __reachable_tiles_helper(self, base_position: Position) -> Set[Position]:
        """
        Given a base Position, gets a Set of reachable Positions on this Board
        :param base_position: the Position representing the start Position for the search
        :return: a Set of all reachable Positions including the base Position
        """
        stack = [base_position]
        acc_positions: Set[Position] = {base_position}
        while stack:
            curr_position = stack.pop()
            for neighbor in self.__check_neighbors(curr_position, acc_positions):
                stack.append(neighbor)
                acc_positions.add(neighbor)
        return acc_positions

    def __connected_tile(self, base_tile: Tile, neighbor_tile: Tile, base_path: Direction) -> bool:
        """
        Checks if the two given Tiles are connected by the given Direction on the base Tile
        :param base_tile: The source Tile to check the connection of
        :param neighbor_tile: The neighbor Tile to check the connection of
        :param base_path: A Direction representing the Direction to check from the base_tile
        :return: A Tile, if the function finds a connected neighbor, it will return the neighbor. If it does not,
        it will return the given base Tile
        """
        neighbor_path = base_path.get_opposite_direction()
        return base_tile.has_path(base_path) and neighbor_tile.has_path(neighbor_path)

    def __check_neighbors(self, base_position: Position, acc_positions: Set[Position]) -> List[Position]:
        """
        Gets all the given Position's connected neighbors (adjacent tiles which are connected to it via paths)
        :param base_position: A Position representing the source Position to search from
        :return: A List of Positions representing, all connected neighbors to the given base Position
        """
        connected_neighbors: List[Position] = []
        base_row = base_position.get_row()
        base_col = base_position.get_col()
        base_tile = self.__tile_grid[base_row][base_col]
        for direction in Direction:
            row_offset, col_offset = direction.get_offset_tuple()
            neighbor_row = base_row + row_offset
            neighbor_col = base_col + col_offset
            neighbor_pos = Position(neighbor_row, neighbor_col)
            if neighbor_pos not in acc_positions and self.__valid_tile_location(neighbor_row, neighbor_col):
                neighbor_tile = self.__tile_grid[neighbor_row][neighbor_col]
                if self.__connected_tile(base_tile, neighbor_tile, direction):
                    connected_neighbors.append(neighbor_pos)
        return connected_neighbors

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

    def __valid_tile_location(self, row, col) -> bool:
        """
        Checks if the given indices are within the bounds of the board
        :param row: An int representing the row of the potential Tile
        :param col: An int representing the column of the potential Tile
        :return: True if the supplied indices are within the board, False otherwise
        """
        return (0 <= row < self.__height) and (0 <= col < self.__width)

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

    def __eq__(self, other: Any) -> bool:
        """
        Overrides equals to see if this Board is the same as the given other object
        :param other: object being compared to this Board
        :return: True if this Board is the same as the given object, otherwise False
        """
        if isinstance(other, Board):
            if self.__height == other.__height and self.__width == other.__width:
                for row in range(self.__height):
                    for col in range(self.__width):
                        if self.__tile_grid[row][col] != other.__tile_grid[row][col]:
                            return False
                return self.__next_tile == other.__next_tile
        return False
