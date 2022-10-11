from tile import Tile


class Player:
    def __init__(self, home_tile: Tile, goal_tile: Tile, current_tile: Tile):
        self.__home_tile = home_tile
        self.__goal_tile = goal_tile
        self.__current_tile = current_tile

    def get_home_tile(self):
        return self.__home_tile

    def get_goal_tile(self):
        return self.__goal_tile

    def get_current_tile(self):
        return self.__current_tile
