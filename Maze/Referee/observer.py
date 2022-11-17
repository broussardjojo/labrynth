from abc import abstractmethod, ABC

from Maze.Common.state import State


class Observer(ABC):
    """
    Represents an Observer for a game of Labyrinth. An observer can display a given State of the game.
    """

    @abstractmethod
    def receive_new_state(self, next_state: State) -> None:
        """
        Takes in a State to be observed.
        :param next_state: a State representing the state of the game to be observed
        :return: None
        """

    @abstractmethod
    def set_game_is_over(self) -> None:
        """
        Declares that the game being observed is over
        :return: None
        """

    @abstractmethod
    def update_gui(self) -> bool:
        """
        Updates the window to display the latest state
        :return: True if the app should continue to send updates, False otherwise (meaning the user has quit)
        """