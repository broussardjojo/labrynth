from ..Common.direction import Direction
from ..Common.position import Position
from abc import ABC, abstractmethod


class Move(ABC):
    @abstractmethod
    def is_pass(self):
        pass


class PassMove(Move):
    def is_pass(self):
        return True


class ValidMove(Move):
    def is_pass(self):
        return False

    def __init__(self, slide_index: int, slide_direction: Direction, spare_tile_rotation_degrees: int,
                 destination_position: Position):
        self.__slide_index = slide_index
        self.__slide_direction = slide_direction
        self.__spare_tile_rotation_degrees = spare_tile_rotation_degrees
        self.__destination_position = destination_position

    def get_slide_index(self):
        return self.__slide_index

    def get_slide_direction(self):
        return self.__slide_direction

    def get_spare_tile_rotation_degrees(self):
        return self.__spare_tile_rotation_degrees

    def get_destination_position(self):
        return self.__destination_position
