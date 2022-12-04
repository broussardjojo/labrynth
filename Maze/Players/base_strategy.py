from abc import abstractmethod
from typing import Union, Tuple, Iterator, Set, Dict

from Maze.Common.direction import Direction
from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Players.move import Move, Pass
from Maze.Players.strategy import Strategy

FULL_ROTATION = 4
RotateAndSlide = Tuple[int, int, Direction]


class BaseStrategy(Strategy):
    """
    A BaseStrategy representing a general type of strategy which picks a target and tries every possible slide/insert
    and rotate to see if it's possible to reach it, then gets a new target and repeats, passing if there are no
    more targets to try.
    """

    def __init__(self):
        """
        Constructor for a BaseStrategy which initializes the __checked_positions list to an empty list because no
        positions have been checked yet.
        """
        self.__checked_positions = []

    def get_legal_slides(self, state: RedactedState) -> Iterator[Tuple[int, Direction]]:
        """
        Creates an iterator of the legal slides, ordered by the follow criteria:
            - Direction - Horizontal < Vertical
            - Increasing index
            - Direction - Left < Right | Up < Down
        :param state: The current state to search for legal slides on.
        :return: an ordered iterable of legal slide moves for the active player to perform.
        """
        for row in range(state.get_board().get_height()):
            for direction in Direction.horizontal_directions():
                if state.is_legal_slide_action((row, direction)):
                    yield (row, direction)

        for col in range(state.get_board().get_width()):
            for direction in Direction.vertical_directions():
                if state.is_legal_slide_action((col, direction)):
                    yield (col, direction)

    @abstractmethod
    def get_goals(self, state: RedactedState, primary_goal: Position) -> Iterator[Position]:
        """
        Creates an iterator of the immediate and alternative goals for the active player, in order of their preference.
        :param state:
        :param primary_goal:
        :return:  an ordered iterable of goal positions for the active player to try to reach on this move.
        """

    def get_legal_destinations_after_rotate_and_slide(self,
                                                      current_state: RedactedState,
                                                      rotation: int,
                                                      slide: Tuple[int, Direction],
                                                      cache: Dict[RotateAndSlide, Set[Position]]) -> Set[Position]:
        """
        Returns the set of reachable positions which are legal for the active player to end their turn on given a
        starting state, a number of right-angle clockwise rotations, and a slide.
        :param current_state: The current state to get legal destinations on.
        :param rotation: The number of clockwise 90 degree rotations to rotate the spare - expected to be 0, 1, 2, or 3.
        :param slide: The slide to perform before checking for legal destinations.
        :param cache: Saved results from previous calls on this same state.
        :return: The set of reachable positions which are legal to end turn on given the slide and rotation are
            performed.
        """
        # Check cache to see if we've already performed this move
        key: RotateAndSlide = (rotation, slide[0], slide[1])
        if key in cache:
            return cache[key]

        # Perform the move and save it in the cache
        # This explorable state allows a player to try illegal moves without being kicked
        with current_state.exploration_context(90*rotation, slide):
            result = current_state.get_legal_destinations()
            cache[key] = result

        return result

    def get_rotations(self) -> Iterator[int]:
        """
        Yield legal spare tile rotations to try.

        The default implementation tries the four rotations in counterclockwise order.
        :return: An iterator over rotations, each of which is a number of right angle clockwise rotations.
        """
        yield from [0, 3, 2, 1]

    def generate_move(self, current_state: RedactedState, target_position: Position) -> Union[Move, Pass]:
        """
        Returns the first move found that the active player can legally make that satisfies their most preferable
        reachable goal.

        Moves are tested according to their destination's order in self.get_goals(), and for each destination,
        self.get_legal_slides() determines the preference order for slides.
        :param current_state: The
        :param target_position:
        :return:
        """
        cache: Dict[RotateAndSlide, Set[Position]] = {}
        for goal in self.get_goals(current_state, target_position):
            for slide in self.get_legal_slides(current_state):
                for rotation in self.get_rotations():
                    legal_destinations = self.get_legal_destinations_after_rotate_and_slide(
                        current_state, rotation, slide, cache
                    )
                    if goal in legal_destinations:
                        return Move(slide[0], slide[1], 90 * rotation, goal)
        return Pass()
