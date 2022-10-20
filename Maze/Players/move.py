from ..Common.direction import Direction
from ..Common.position import Position


class Move:
    def __init__(self, slide_index: int, slide_direction: Direction, spare_tile_rotation_degrees: int,
                 destination_position: Position, pass_move: bool):
        self.__slide_index = slide_index
        self.__slide_direction = slide_direction
        self.__spare_tile_rotation_degrees = spare_tile_rotation_degrees
        self.__destination_position = destination_position
        self.__pass_move = pass_move

    def is_pass(self):
        return self.__pass_move

    def get_slide_index(self):
        if self.is_pass():
            raise ValueError("Cannot access slide index of a pass move")
        return self.__slide_index

    def get_slide_direction(self):
        if self.is_pass():
            raise ValueError("Cannot access slide direction of a pass move")
        return self.__slide_direction

    def get_spare_tile_rotation_degrees(self):
        if self.is_pass():
            raise ValueError("Cannot access degree of a pass move")
        return self.__spare_tile_rotation_degrees

    def get_destination_position(self):
        if self.is_pass():
            raise ValueError("Cannot access destination of a pass move")
        return self.__destination_position

    def __eq__(self, other):
        if isinstance(other, Move):
            return other.__slide_index == self.__slide_index \
                   and other.__slide_direction == self.__slide_direction \
                   and other.__pass_move == self.__pass_move \
                   and other.__spare_tile_rotation_degrees == self.__spare_tile_rotation_degrees \
                   and other.__destination_position == self.__destination_position
        return False

    def __str__(self):
        return f"Index: {self.__slide_index}, Direction: {self.__slide_direction}, Spare Rotation: " \
               f"{self.__spare_tile_rotation_degrees}, Destination: {self.__destination_position}, " \
               f"Pass: {self.__pass_move}"
