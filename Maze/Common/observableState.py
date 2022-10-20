from .board import Board


class ObservableState:
    """
    Base class for a State which only exposes information to untrusted users of this class. It does not give access to
    Player information or allow users to change the Board for this State.
    """

    def __init__(self, board: Board):
        """
        A constructor for a State, taking in a Board which represents the board for a game of Labyrinth.
        :param board: a Board representing the board for a game of Labyrinth
        """
        self.__board = board

    def get_board(self) -> Board:
        """
        Gets the __board in this State
        :return: a Board representing this State's board
        """
        return self.__board
