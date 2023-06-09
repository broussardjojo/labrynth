from Maze.Common.player_details import PlayerDetails
from Maze.Common.position import Position
from Maze.Common.utils import get_euclidean_distance_between


class RefereePlayerDetails(PlayerDetails):
    """
    A RefereePlayerDetails is a representation of a player of a game of Labyrinth that has a goal position,
    in addition to the home position, current position, and color from PlayerDetails
    """

    _home_position: Position
    _goal_position: Position
    _current_position: Position
    _color: str
    _is_goal_ultimate: bool

    def __init__(self, home_position: Position, goal_position: Position,
                 current_position: Position, color: str):
        """
        A Constructor for a Player which assigns the provided home, goal, and current Positions to the respective fields
        :param home_position: the Position of this Player's home Tile where they begin the game
        :param goal_position: the Position of this Player's goal Tile
        :param current_position: the current Position of this Player
        :param color: the color that this Player will use; can be a hexcode RGB value or a color name
        """
        super().__init__(home_position, current_position, color)
        self._goal_position = goal_position
        self._is_goal_ultimate = False

    @classmethod
    def from_home_goal_color(cls, home_position: Position, goal_position: Position,
                             color: str) -> "RefereePlayerDetails":
        """
        Constructor to create a Player from a given goal position, home position, and color
        :param home_position: a Position representing the home Position of this Player
        :param goal_position: a Position representing the goal Position of this Player
        :param color: a string representing the color of this Player's avatar
        :return: an instance of a Player
        """
        current_position = home_position
        return cls(home_position, goal_position, current_position, color)

    @classmethod
    def from_current_home_color(cls, current_position: Position, home_position: Position,
                                color: str) -> "RefereePlayerDetails":
        """
        Constructor to create a Player given a current position, home position, and color
        TODO: makes an arbitrary decision to assigns the Player's goal to its current Position
        :param current_position: a Position representing the current Position of this Player
        :param home_position: a Position representing the home Position of this Player
        :param color: a string representing the color of this Player's avatar
        :return: an instance of a Player
        """
        goal_position = current_position
        return cls(home_position, goal_position, current_position, color)

    def get_goal_position(self) -> Position:
        """
        Getter for __goal_position
        :return: a Position representing the location of this Player's goal on a Board
        """
        return self._goal_position

    def is_goal_ultimate(self) -> bool:
        """
        Returns if the player's goal will not be followed by subsequent assignments.
        :return: True if the player's goal is their last one they will be assigned.
        """
        return self._is_goal_ultimate

    def set_goal_position(self, new_position: Position, is_ultimate: bool = False) -> None:
        """
        Setter for __goal_position.
        :param new_position: The position the player should now move towards.
        :param is_ultimate: A boolean flag to determine if there will not be another goal assigned after reaching this
            one.
        :return: None
        """
        self._goal_position = new_position
        self._is_goal_ultimate = is_ultimate


    def copy_without_secrets(self) -> PlayerDetails:
        """
        Copies this player's public information to a new object
        :return: a PlayerDetails
        """
        return PlayerDetails(self._home_position, self._current_position, self._color)

    def get_euclidean_distance_from_current_to_goal(self) -> int:
        """
        Return the SQUARED euclidean distance of this player's current position to their next goal.
        :return: An integer representing the squared euclidean distance of the player to their next goal.
        """
        return get_euclidean_distance_between(self._current_position, self._goal_position)
