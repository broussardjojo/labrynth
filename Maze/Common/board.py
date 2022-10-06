from typing import List
from tile import Tile
from gem import Gem
from shapes import Shape, Line, Corner, TShaped, Cross
from utils import generate_gem_list
import random


class Board:
    def __init__(self, dimensions: int):
        gem_name_list = generate_gem_list()
        self.__tile_grid = []
        self.__initialize_board(gem_name_list, dimensions)
        self.__next_tile = self.__generate_unique_tile(gem_name_list)

    def __initialize_board(self, gem_name_list: List[str], dimension: int) -> None:
        for row in range(dimension):
            self.__tile_grid.append([])
            for column in range(dimension):
                unique_tile = self.__generate_unique_tile(gem_name_list)
                self.__tile_grid[row].append(unique_tile)

    def __generate_unique_tile(self, gem_name_list: List[str]) -> Tile:
        potential_tile = Tile(self.__get_random_shape(),
                              self.__get_random_gem(gem_name_list),
                              self.__get_random_gem(gem_name_list))
        for row in self.__tile_grid:
            for tile in row:
                if tile.get_gems() == potential_tile.get_gems():
                    return self.__generate_unique_tile(gem_name_list)
        return potential_tile

    @staticmethod
    def __get_random_shape() -> Shape:
        all_shape_dict = {
            0: Line(0),
            1: Corner(0),
            2: TShaped(0),
            3: Cross()
        }
        random_shape = all_shape_dict[random.randint(0, len(all_shape_dict))]
        return random_shape

    @staticmethod
    def __get_random_gem(gem_name_list: List[str]) -> Gem:
        return Gem(gem_name_list[random.randint(0, len(gem_name_list))])
