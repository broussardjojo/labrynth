import itertools
import logging
import random
from collections import deque
from concurrent.futures import Executor, ThreadPoolExecutor, Future
from copy import deepcopy
from enum import Enum, auto
from typing import List, Tuple, Any, ClassVar, Optional, Deque

from Maze.Common.board import Board
from Maze.Common.position import Position
from Maze.Common.referee_player_details import RefereePlayerDetails
from Maze.Common.state import State
from Maze.Common.thread_utils import gather_protected, await_protected
from Maze.Common.utils import ALL_NAMED_COLORS, Maybe
from Maze.Players.api_player import APIPlayer
from Maze.Players.move import Move, Pass
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Referee.observer import Observer
from Maze.config import CONFIG

log = logging.getLogger(__name__)

# A pair of lists of APIPlayers; the first list represents all winners,
# the second represents all ejected players
GameOutcome = Tuple[List[APIPlayer], List[APIPlayer]]


class MoveReturnType(Enum):
    """
    An enumeration to represent the various outcomes of a player's turn.
    Ejections are performed by the caller when the run turn method returns `KICK`, but moves and passes are performed
    within the run turn method.
    """
    PASSED = auto()
    MOVED = auto()
    KICK = auto()

class RoundReturnType(Enum):
    """
    An enumeration to represent the various outcomes of a round.
    """
    DEFAULT = auto()  # We continue running the game
    NO_MOVES_MADE = auto()  # All players that are in the game opted to pass
    PLAYER_REACHED_HOME = auto()  # A player terminated the game by reaching their ultimate goal



class Referee:
    """
    A class representing a Referee for a game of Labyrinth. A referee is an arbiter of the game and is responsible for
    running the game to completion. The referee can handle the following abnormal interactions:
    - Player taking too long to propose a Move
    - Player provides invalid rotate
    - Player provides invalid slide
    - Player provides a slide-insert interaction that undoes the previous Move
    - Player provides a destination that is not on the board
    - Player provides a destination they cannot reach using their proposed Move
    We leave the following abnormal interactions to the remote communication phase of the game:
    - Player taking too long to propose a Board
    - Player proposing invalid Board (either invalid size or invalid by some future determination i.e. "unfair" or bad
    for game play)
    """

    __cheating_players: List[SafeAPIPlayer]
    __winning_players: List[SafeAPIPlayer]
    __current_players: List[SafeAPIPlayer]
    __additional_goals: Deque[Position]

    __random: random.Random
    __observers: List[Observer]
    __created_own_executor: bool
    executor: Executor
    __timeout_seconds: float

    def __init__(self, executor: Optional[ThreadPoolExecutor] = None, random_seed: Optional[int] = None):
        """
        Creates an instance of a Referee given a game State
        """
        self.__random = random.Random()
        if random_seed is not None:
            self.__random.seed(random_seed)
        self.__observers = []
        self.executor = executor if (executor is not None) else ThreadPoolExecutor(max_workers=32)
        self.__created_own_executor = executor is None
        self.__timeout_seconds = CONFIG.referee_method_call_timeout
        self.__reset_referee()

    def __enter__(self) -> "Referee":
        """
        Overrides the __enter__ method of Referees so that `with Referee() as ref: ...` works
        :return: this Referee
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Overrides the __exit__ method of Referees so that in the case where this Referee made its own
        ThreadPoolExecutor, a `with Referee() as ref: ...` block always ends by closing the executor
        :return: None
        """
        if self.__created_own_executor:
            self.executor.shutdown(wait=False)

    def add_observer(self, observer: Observer) -> None:
        """
        Subscribes an observer to game progress updates from this referee.
        :param observer: An Observer, which will now receive updates
        :return: None
        """
        self.__observers.append(observer)

    def __reset_referee(self) -> None:
        """
        Resets this Referee's fields to their initial states
        :return: None
        """
        self.__cheating_players = []
        self.__winning_players = []
        self.__current_players = []
        self.__additional_goals = deque()

    def run_game(self, players: List[APIPlayer]) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a list of players. It creates a safe version of all
        the players, then creates a State from the given list of players, sets up the game, and runs the game.

        A game consists of rounds (each remaining player taking a turn), until one of the completion criteria is met:
        1. a player reaches its home (also refereed to as its ultimate goal) after visiting its all of its goal tiles;
        2. all players that survive a round opt to pass
        3. the referee has run 1000 rounds

        :param players: the list of players for a game of Labyrinth
        :return: A List of winning APIPlayers representing either the winner or all players who tied for the win and
        a List of cheating APIPlayers representing all APIPlayers who were kicked out for cheating.
        """
        safe_players = [SafeAPIPlayer(client, self.executor) for client in players]
        return self.run_game_with_safe_players(safe_players)

    def run_game_with_safe_players(self, players: List[SafeAPIPlayer]) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a list of players. It creates a State from the given list
        of players, sets up the game, and then runs the game.
        :param players: the list of players for a game of Labyrinth
        :return: A List of winning APIPlayers representing either the winner or all players who tied for the win and
        a List of cheating APIPlayers representing all APIPlayers who were kicked out for cheating.
        """
        selected_board = self.get_proposed_board(players)
        player_details, additional_goals = self.__generate_players(selected_board, len(players))
        game_state = State.from_board_and_players(selected_board, player_details)
        return self.run_game_with_safe_players_and_goals(players, game_state, additional_goals)

    def run_game_from_state(self, players: List[APIPlayer], game_state: State) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a game state. It creates a safe version of all
        the players, then sets up and runs the game.
        :param players: the list of players for a game of Labyrinth
        :param game_state: the state for a game of Labyrinth
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating
        :raises: ValueError if the number of APIPlayers does not match the amount of players in the game state.
        """
        safe_players = [SafeAPIPlayer(client, self.executor) for client in players]
        return self.run_game_with_safe_players_from_state(safe_players, game_state)

    def run_game_with_safe_players_from_state(self, players: List[SafeAPIPlayer], game_state: State) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a game state and SafeAPIPlayer list. It sets up
        players and runs the game.
        :param players: the list of players for a game of Labyrinth
        :param game_state: the state for a game of Labyrinth
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating
        :raises: ValueError if the number of SafeAPIPlayers does not match the amount of players in the game state.
        """
        additional_goals = self.__generate_additional_goals_from_state(game_state)
        return self.run_game_with_safe_players_and_goals(players, game_state, additional_goals)

    def run_game_with_safe_players_and_goals(self, players: List[SafeAPIPlayer], game_state: State,
                                             additional_goals: List[Position]) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a SafeAPIPlayer list, game state, and list of additional
        goals. It sets up players and runs the game.
        :param players: the list of players for a game of Labyrinth
        :param game_state: the state for a game of Labyrinth
        :param additional_goals: the ordered sequence of treasure goals, handed out when a
        player has reached a goal and needs another one
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating
        :raises: ValueError if the number of SafeAPIPlayers does not match the amount of players in the game state.
        """
        if len(players) != len(game_state.get_players()):
            raise ValueError(f"Number of APIPlayers ({len(players)}) does not match number of players "
                             f"in game state ({len(game_state.get_players())})")

        self.__reset_referee()
        self.__additional_goals = deque(additional_goals)
        self.__current_players = players.copy()
        self.__setup(game_state)
        winners, cheaters = self.__run_rounds_until_game_over(game_state)
        unwrapped_winners = [safe_api_player.player for safe_api_player in winners]
        unwrapped_cheaters = [safe_api_player.player for safe_api_player in cheaters]
        return unwrapped_winners, unwrapped_cheaters

    def __run_rounds_until_game_over(self, game_state: State) -> Tuple[List[SafeAPIPlayer], List[SafeAPIPlayer]]:
        """
        Method to run a game of Labyrinth, this method will run until the game is over, for each player in the list
        it will request a move, validate the move, perform the move or kick the player out, and check if the game is
        over. At the end, the referee will inform all winning APIPlayers that they have won and return a list of winning
        APIPlayers and a List of cheating APIPlayers
        :return: A List of winning APIPlayers representing either the winner or all players who tied for the win and
        a List of cheating APIPlayers representing all APIPlayers who were kicked out for cheating.
        """
        self.send_state_updates_to_observers(game_state)
        current_round = 0
        round_status = RoundReturnType.DEFAULT
        while current_round < CONFIG.referee_max_rounds and round_status is RoundReturnType.DEFAULT:
            round_status = self.__run_round(game_state)
            current_round += 1
        winning_players = game_state.get_closest_players_to_victory(
            did_active_player_move=round_status is RoundReturnType.PLAYER_REACHED_HOME
        )
        self.__inform_winning_players(game_state, winning_players)
        self.send_game_over_to_observers()
        return self.__winning_players, self.__cheating_players

    def __run_round(self, game_state: State) -> RoundReturnType:
        """
        Runs a round of a game. A round is considered complete when all players have taken a turn.
        :param game_state: represents the current state of the game
        :return: True if the game is over, otherwise False
        """
        any_player_moved = False
        num_players = len(self.__current_players)
        for _ in range(num_players):
            move_outcome = self.__run_active_player_turn(game_state)
            any_player_moved |= move_outcome is MoveReturnType.MOVED
            if move_outcome is MoveReturnType.MOVED:
                goal_reached = game_state.update_active_player_goals_reached()
                if game_state.is_active_player_at_ultimate_goal():
                    self.send_state_updates_to_observers(game_state)
                    return RoundReturnType.PLAYER_REACHED_HOME
                if goal_reached:
                    setup_response = self.__inform_player_of_new_goal(game_state)
                    if not setup_response:
                        move_outcome = MoveReturnType.KICK

            if move_outcome is MoveReturnType.KICK:
                self.__handle_cheater(self.__current_players[game_state.get_active_player_index()], game_state)
            else:
                game_state.change_active_player_turn()

            self.send_state_updates_to_observers(game_state)

        # Round completed normally, the game is only over if no players moved during this round
        if not any_player_moved:
            return RoundReturnType.NO_MOVES_MADE
        return RoundReturnType.DEFAULT

    def get_proposed_board(self, clients: List[SafeAPIPlayer]) -> Board:
        """
        Gets a Board from APIPlayers' proposals
        NOTE: this method is mainly defined for testing at this point, we will implement it fully when it is required
        :param clients: the list of APIPlayers allowed to propose a Board
        :return: a randomly selected Board from the list of proposed Boards
        """
        for dimension in itertools.count(start=7, step=2):
            if Board.number_of_stationary_positions(dimension, dimension) >= len(clients):
                return Board.from_random_board(dimension, dimension, rand=self.__random)
        raise RuntimeError("This line should be unreachable")

    def __handle_cheater(self, active_player: SafeAPIPlayer, game_state: State) -> None:
        """
        Kicks the given player out of the game and adds them to a list of cheating players.
        :param active_player: the player found cheating
        :return: None
        side effect: mutates the cheater_players list, mutates the game_state by kicking out the active player
        """
        self.__current_players.remove(active_player)
        game_state.kick_out_active_player()
        self.__cheating_players.append(active_player)
        log.info(f"Kicked player {active_player.name()}")
        active_player.on_kicked()

    def __handle_broadcast_acknowledgements(self, responses: List[Maybe[Any]], game_state: State) -> None:
        """
        Kicks out all players who failed to acknowledge a broadcast, based on the given response list
        :param responses: A list of Maybe[Any] objects; each element represents the response of the corresponding
        APIPlayer in __current_players
        :return: None
        :raises: ValueError if len(responses) doesn't equal the number of current players
        """
        num_players = len(self.__current_players)
        if len(responses) != num_players:
            raise ValueError("Error: Incorrect broadcast response list")
        current_player_index = game_state.get_active_player_index()
        responses_in_game_order = [*responses[current_player_index:], *responses[:current_player_index]]
        for response in responses_in_game_order:
            if not response.is_present:
                # active client didn't send an acknowledgment
                active_client = self.__current_players[game_state.get_active_player_index()]
                self.__handle_cheater(active_client, game_state)
            else:
                game_state.change_active_player_turn()

    def __setup(self, game_state: State) -> None:
        """
        Method to give each player their goal Tile, players who fail to acknowledge in DEFAULT_TIMEOUT_SECONDS
         will be deemed to be cheating
        :param: game_state: The game state to broadcast to players after redaction.
        :return: None
        Side effect: Adds to self.__cheating_players and removes from self.__current_players
            any player who fails to acknowledge the 'setup' call.
        """
        future_list: "List[Future[Any]]" = []
        for index, (client, player) in enumerate(zip(self.__current_players, game_state.get_players())):
            state_copy = game_state.copy_redacted(active_player_index=index)
            future = client.setup(state_copy, player.get_goal_position())
            future_list.append(future)
        log.info("Broadcast setup start")
        responses = gather_protected(future_list, timeout_seconds=self.__timeout_seconds, debug=True)
        log.info("Broadcast setup end")
        self.__handle_broadcast_acknowledgements(responses, game_state)

    def __generate_players(self, board: Board, count: int) -> Tuple[List[RefereePlayerDetails], List[Position]]:
        """
        Generates the initial info (home, goal, current, color) for a given number of players on a given board, and
        returns it with the list of positions NOT used as initial goals for the players.
        :param board: The Board to prepare players for
        :param count: The number of player information pieces to create
        :return: A tuple with the first element a list of Player instances with unique homes, and the second element
            a list of Positions not used as goals for the created players.
        """
        players: List[RefereePlayerDetails] = []

        homes = self.__generate_homes(board, count)
        initial_goals, additional_goals = self.__generate_initial_and_additional_goals(board, count)
        colors = self.__generate_colors(count)

        for home, initial_goal, color in zip(homes, initial_goals, colors):
            player = RefereePlayerDetails.from_home_goal_color(home, initial_goal, color)
            players.append(player)

        return players, additional_goals

    @staticmethod
    def __generate_colors(count: int) -> List[str]:
        """
        Generate a unique color for each player in the game.
        :param count: The number of players to generate colors for.
        :return: A list of strings representing the colors of each player in the game.
        """
        result = ALL_NAMED_COLORS.copy()
        while len(result) < count:
            result.append(str(len(result)).zfill(6))
        return result[:count]

    def __generate_homes(self, board: Board, count: int) -> List[Position]:
        """
        Method to generate a unique home Position for all players in the game
        :param board: The Board on which the player's home should be placed
        :param count: The number of Positions to generate as homes.
        :return: A list of Positions representing the unique home Position for each player to use
        :raises: ValueError if there are not enough unique home tiles.
        TODO: Test this
        """
        stationary_positions = board.get_all_stationary_positions()

        if count > len(stationary_positions):
            raise ValueError(f"Not enough stationary positions ({len(stationary_positions)}) to assign unique homes"
                             f" to all players ({count})")
        self.__random.shuffle(stationary_positions)
        return stationary_positions[:count]

    def __generate_initial_and_additional_goals(self, board: Board,
                                                count: int) -> Tuple[List[Position], List[Position]]:
        """
        Method to generate sequences of both the initial goals and additional goals.
        If the referee is not configured to use additional goals, return a tuple whose first element is a list of count
        non-unique positions to assign as player goals, and an empty list to be used as additional goals.
        :param board: The Board of which to generate goals for.
        :return: A tuple of Lists of Positions - the first element of the tuple is the positions to be assigned as
            initial goals, and the second is the positions to be assigned as additional goals.
        """
        stationary_positions = board.get_all_stationary_positions()

        if CONFIG.referee_use_additional_goals:
            if count > len(stationary_positions):
                raise ValueError(f"Not enough stationary positions ({len(stationary_positions)}) to assign unique goals"
                                 f"to all players ({count})")
            self.__random.shuffle(stationary_positions)
            return stationary_positions[:count], stationary_positions[count:]
        else:
            return self.__random.choices(stationary_positions, k=count), []

    def __generate_additional_goals_from_state(self, game_state: State) -> List[Position]:
        """
        Method to generate a list of additional goals from a game state that already has assigned players initial goals.
        If the referee is not configured to use additional goals, return an empty list.
        :param game_state: The State for which to generate additional goals for.
        :return: A list of Positions to be used as additional goals.
        """
        if CONFIG.referee_use_additional_goals:
            initial_goals = {player.get_goal_position() for player in game_state.get_players()}
            additional_goals = [position for position in game_state.get_board().get_all_stationary_positions()
                                if position not in initial_goals]
            self.__random.shuffle(additional_goals)
            return additional_goals
        else:
            return []

    def __inform_player_of_new_goal(self, game_state: State) -> bool:
        """
        Assigns the active game state player a new goal and informs the active API player of that goal
        :param game_state: The game state _after_ the active player's move.
        :return: True if the setup call succeeded, False otherwise
        """
        active_api_player = self.__current_players[game_state.get_active_player_index()]
        active_game_state_player = game_state.get_active_player()
        self.__assign_next_goal_position(active_game_state_player)
        log.info("Send:%s setup start", active_api_player.name())
        response = await_protected(
            active_api_player.setup(None, active_game_state_player.get_goal_position()),
            timeout_seconds=self.__timeout_seconds
        )
        log.info("Send:%s setup end", active_api_player.name())
        return response.is_present

    def __inform_winning_players(self, game_state: State, winning_players: List[RefereePlayerDetails]) -> None:
        """
        Tells all winning players they have won the game
        :param game_state: The game state
        :param winning_players: The list of RefereePlayerDetails who have won the game.
        :return: None
        Side effect: Adds to self.__cheating_players and removes from self.__current_players
            any player who fails to acknowledge the 'win' call.
        Side effect: Sets self.__winning_players.
        """
        future_list: "List[Future[Any]]" = []
        for client, player in zip(self.__current_players, game_state.get_players()):
            did_win = player in winning_players
            future = client.win(did_win)
            future_list.append(future)
        log.info("Broadcast win start")
        responses = gather_protected(future_list, timeout_seconds=self.__timeout_seconds, debug=True)
        log.info("Broadcast win end")
        # clients that fail to acknowledge will be moved from current players to cheater players by this method
        # clients which are still in current_players are the only candidates for the GameOutcome winners
        self.__handle_broadcast_acknowledgements(responses, game_state)
        self.__winning_players = [client for client, player in zip(self.__current_players, game_state.get_players())
                                  if player in winning_players]

    def __is_valid_move(self, proposed_move: Move, game_state: State) -> bool:
        """
        A method to validate the proposed move has a valid slide and insert for the current game state, and has a
        valid destination position for the active player in the game state after performing the given move.
        :param proposed_move: The proposed Move to perform
        :param game_state: The game state to check the provided Move
        :return: True if the move is valid, False otherwise
        """
        slide_action = (proposed_move.get_slide_index(), proposed_move.get_slide_direction())
        if proposed_move.get_spare_tile_rotation_degrees() % 90 != 0:
            return False
        if not game_state.is_legal_slide_action(slide_action):
            return False
        with game_state.exploration_context(proposed_move.get_spare_tile_rotation_degrees(), slide_action):
            return proposed_move.get_destination_position() in game_state.get_legal_destinations()

    def __perform_valid_move(self, proposed_move: Move, game_state: State) -> None:
        """
        Perform a validated move by rotating, sliding and inserting, and moving.
        :param proposed_move: The Move to make
        :param game_state: The game state from which to make the move
        :return: None
        """
        game_state.rotate_spare_tile(proposed_move.get_spare_tile_rotation_degrees())
        game_state.slide_and_insert(proposed_move.get_slide_index(),
                                    proposed_move.get_slide_direction())
        game_state.move_active_player_to(proposed_move.get_destination_position())

    def __assign_next_goal_position(self, player_details: RefereePlayerDetails) -> None:
        """
        Assigns the position of the next goal assignment for the given player.
        This can be the position of another treasure or of the player's home if there are no more additional goals.
        :param player_details: The player to return a goal assignment for.
        Side effect: If there are remaining goals in the referee's additional goals, this method removes the leftmost.
        """
        if len(self.__additional_goals) > 0:
            player_details.set_goal_position(self.__additional_goals.popleft())
        else:
            player_details.set_goal_position(player_details.get_home_position(), is_ultimate=True)

    def __run_active_player_turn(self, game_state: State) -> MoveReturnType:
        """
        Runs a single player turn within a game given the current game state
        :param game_state: represents the current state of the game
        :return: True if the player moves legally, otherwise False
        """
        player_index = game_state.get_active_player_index()
        client = self.__current_players[player_index]
        log.info("Send:%s take_turn start", client.name())
        response = await_protected(client.take_turn(game_state.copy_redacted()), timeout_seconds=self.__timeout_seconds)
        log.info("Send:%s take_turn end %r", client.name(), response)
        if not response.is_present:
            return MoveReturnType.KICK
        proposed_move = response.get()

        if isinstance(proposed_move, Pass):
            return MoveReturnType.PASSED
        if not self.__is_valid_move(proposed_move, game_state):
            return MoveReturnType.KICK
        self.__perform_valid_move(proposed_move, game_state)
        return MoveReturnType.MOVED

    def send_state_updates_to_observers(self, game_state: State) -> None:
        """
        Updates all subscribed observers when a game of Labyrinth has a new state.
        Note: misbehaving observers are not kicked out of the list
        :return: None
        """
        future_list = [
            self.executor.submit(observer.receive_new_state, deepcopy(game_state))
            for observer in self.__observers
        ]
        gather_protected(future_list, timeout_seconds=self.__timeout_seconds)

    def send_game_over_to_observers(self) -> None:
        """
        Updates all subscribed observers when a game of Labyrinth finishes.
        Note: misbehaving observers are not kicked out of the list
        :return: None
        """
        future_list = [
            self.executor.submit(observer.set_game_is_over)
            for observer in self.__observers
        ]
        gather_protected(future_list, timeout_seconds=self.__timeout_seconds)
