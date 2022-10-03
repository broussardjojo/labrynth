class Tile:
    def __init__(self, top: bool, bottom: bool, left: bool, right: bool):
        """
        This constructor creates a Tile with four paths.
        :param top: boolean representing whether or not the top path exists
        :param bottom: boolean representing whether or not the bottom path exists
        :param left: boolean representing whether or not the left path exists
        :param right: boolean representing whether or not the right path exists
        """

        if self.__check_valid_tile(top, bottom, left, right):
            self.top = top
            self.bottom = bottom
            self.left = left
            self.right = right
        else:
            raise ValueError("Invalid tile")

    def __check_valid_tile(self, top: bool, bottom: bool, left: bool, right: bool):
        return sum([top, bottom, left, right]) >= 2

    def rotate(self, rotations: int):
        """
        This method rotates this tile n times, where n is the number of rotations passed in.
        side effect: mutates the tile's paths
        :param rotations: int which represents the number of 90 degree rotations to perform on the tile, must be a
        positive number
        :return: None
        """
        for i in range(rotations):
            self.__rotate_helper()

    def __rotate_helper(self):
        """
        This method rotates this tile 90 degrees to the right
        side effect: mutates the tile's paths
        :return: None
        """
        old_top: bool = self.top
        old_bottom: bool = self.bottom
        old_left: bool = self.left
        old_right: bool = self.right

        self.top = old_left
        self.right = old_top
        self.bottom = old_right
        self.left = old_bottom


    def __eq__(self, other):
        if isinstance(other, Tile):
            return self.right == other.right and self.left == other.left \
                   and self.top == other.top and self.bottom == other.bottom
        return False
