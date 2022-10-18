from direction import Direction

class Position:
    def __init__(self, row, col):
        self.__row = row
        self.__col = col

    def get_row(self):
        return self.__row

    def get_col(self):
        return self.__col

    def adjust_position_in_bound(self, slide_index, slide_direction, max_pos):
        print('here')
        print(self.__row)
        print(self.__col)
        if slide_direction == Direction.Up:
            if slide_index == self.__col:
                self.__row = self.__row - 1 if self.__row > 0 else max_pos - 1
        elif slide_direction == Direction.Down:
            if slide_index == self.__col:
                self.__row = self.__row + 1 if self.__row < max_pos - 1 else 0
        elif slide_direction == Direction.Left:
            if slide_index == self.__row:
                self.__col = self.__col - 1 if self.__col > 0 else max_pos - 1
        else:
            if slide_index == self.__row:
                self.__col = self.__col + 1 if self.__col < max_pos - 1 else 0

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.__row == other.__row and self.__col == other.__col
        return False

    def __str__(self):
        return f"({self.__row}, {self.__col})"