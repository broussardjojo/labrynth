class Position:
    """
    Represents a Position on a Board as a row and column, which represent row and column indices on a Board's tile grid,
    a 2-D List of Tiles.
    """
    def __init__(self, row: int, col: int):
        """
        Creates a Position with a row and column representing a coordinate on a Board.
        :param row: an int representing a row index in a Board's 2-D List of Tiles
        :param col: an int representing a column index in a Board's 2-D List of Tiles
        """
        self.__row = row
        self.__col = col

    def get_row(self) -> int:
        """
        Gives the row index for this Position
        :return: an int representing the row index for this Position
        """
        return self.__row

    def get_col(self) -> int:
        """
        Gives the column index for this Position
        :return: an int representing the column index for this Position
        """
        return self.__col

    def __eq__(self, other):
        """
        Overrides equal in order to compare Position objects. A Position is equal to another if they have the same row
        and column integers.
        :param other: The object being compared to this Position
        :return: True if the objects are equal, otherwise false
        """
        if isinstance(other, Position):
            return self.__row == other.__row and self.__col == other.__col
        return False

    def __str__(self):
        """
        Overrides string in order to print Position objects.
        :return: this Position object as a row, col
        """
        return f"({self.__row}, {self.__col})"
