from concurrent.futures import Executor, ThreadPoolExecutor, Future
from copy import deepcopy
from typing import List, Tuple, Set, Any, ClassVar

from .observer import Observer
from ..Common.board import Board
from ..Common.direction import Direction
from ..Common.position import Position
from ..Common.state import State
from ..Common.thread_utils import gather_protected, await_protected, DEFAULT_TIMEOUT
from ..Common.utils import ALL_NAMED_COLORS, Maybe
from ..Players.api_player import APIPlayer
from ..Players.move import Move
from ..Players.player import Player

# A pair of lists of APIPlayers; the first list represents all winners,
# the second represents all ejected players
GameOutcome = Tuple[List[APIPlayer], List[APIPlayer]]


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

    __cheater_players: List[APIPlayer]
    __winning_players: List[APIPlayer]
    __current_players: List[APIPlayer]
    __num_rounds: int
    __timeout_seconds: float
    __did_active_player_cheat: bool

    __observers: List[Observer]
    __executor: Executor
    MAX_ROUNDS: ClassVar[int] = 1000

    def __init__(self, timeout_seconds: float = DEFAULT_TIMEOUT):
        """
        Creates an instance of a Referee given a game State
        """
        self.__observers = []
        self.__executor = ThreadPoolExecutor()
        self.__timeout_seconds = timeout_seconds
        self.__reset_referee()

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
        self.__cheater_players = []
        self.__winning_players = []
        self.__current_players = []
        self.__did_active_player_cheat = False

    def run_game(self, clients: List[APIPlayer]) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a list of players. It creates a State from the given list
        of players, sets up the game, and then runs the game.
        :param clients: the list of players for a game of Labyrinth
        :return: A List of winning APIPlayers representing either the winner or all players who tied for the win and
        a List of cheating APIPlayers representing all APIPlayers who were kicked out for cheating.
        """
        selected_board = self.get_proposed_board(clients)
        players = self.__generate_players(selected_board, len(clients))
        game_state = State.from_board_and_players(selected_board, players)
        return self.run_game_from_state(clients, game_state)

    def run_game_from_state(self, players: List[APIPlayer], game_state: State) -> GameOutcome:
        """
        Entry method that runs a game of Labyrinth when given a game state. It sets up and then runs the game.
        :param players:
        :param game_state: the state for a game of Labyrinth
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating

        NOTE: In this method we create a new Thread which allows us to continue running the functionality necessary for
        run_game in the referee while also displaying a GUI if this referee has an Observer. If we did not create this
        new thread, when the Observer goes to view the state of the game, the GUI program would stop all background
        computation and the Observer would stop receiving any new States from the Referee, even if the game is in
        progress. By creating a new Thread, we can support both functionalities: the Referee running a game, and the
        Observer viewing States from that game. Also note, the mainloop() function from the tkinter GUI library cannot
        be run outside of the main Thread, which is why we create a separate one for running the game and not for
        displaying the GUI.
        """
        self.__reset_referee()
        self.__current_players = players.copy()
        self.__setup(game_state)
        return self.__run_game_helper(game_state)

    def __run_game_helper(self, game_state: State) -> GameOutcome:
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
        is_game_over = False
        while current_round < Referee.MAX_ROUNDS and not is_game_over:
            is_game_over = self.__run_round(game_state)
            current_round += 1
        self.__inform_winning_players(game_state)
        self.send_game_over_to_observers()
        return self.__winning_players, self.__cheater_players

    @staticmethod
    def get_proposed_board(clients: List[APIPlayer]) -> Board:
        """
        Gets a Board from APIPlayers' proposals
        NOTE: this method is mainly defined for testing at this point, we will implement it fully when it is required
        :param clients: the list of APIPlayers allowed to propose a Board
        :return: a randomly selected Board from the list of proposed Boards
        """
        return Board.from_random_board(seed=3)

    def __perform_valid_move(self, proposed_move: Move, game_state: State) -> None:
        """
        Perform a validated move by rotating, sliding and inserting, and moving. Also resets the list of passed APIPlayers
        because this player is not passing.
        :param proposed_move: The Move to make
        :param game_state: The game state from which to make the move
        :return: None
        """
        game_state.rotate_spare_tile(proposed_move.get_spare_tile_rotation_degrees())
        game_state.slide_and_insert(proposed_move.get_slide_index(),
                                    proposed_move.get_slide_direction())
        game_state.move_active_player_to(proposed_move.get_destination_position())
        at_any_goal = game_state.is_active_player_at_goal()
        if at_any_goal and not game_state.did_active_player_win():
            # TODO: parallel ds
            active_api_player = self.__current_players[game_state.get_active_player_index()]
            active_game_state_player = game_state.get_active_player()
            active_api_player.setup(None, active_game_state_player.get_home_position())

    def __perform_move(self, proposed_move: Move, active_player: APIPlayer, game_state: State) -> None:
        """
        Validates the proposed Move by the active APIPlayer. If the move is valid, perform the move, otherwise, kick out
        the active player. If the player passes, add them to the list of passing players
        :param proposed_move: a Move representing the proposed Move to make
        :param active_player: a APIPlayer representing the active player to make this Move
        :return: None
        """
        if self.__is_valid_move(proposed_move, game_state):
            self.__perform_valid_move(proposed_move, game_state)
        else:
            self.__handle_cheater(active_player, game_state)

    def __handle_cheater(self, active_player: APIPlayer, game_state: State) -> None:
        """
        Kicks the given player out of the game and adds them to a list of cheating players.
        :param active_player: the player found cheating
        :return: None
        side effect: mutates the cheater_players list, mutates the game_state by kicking out the active player
        """
        self.__current_players.remove(active_player)
        game_state.kick_out_active_player()
        self.__cheater_players.append(active_player)
        self.__did_active_player_cheat = True

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
        :return: None
        """
        future_list: "List[Future[Any]]" = []
        for client, player in zip(self.__current_players, game_state.get_players()):
            future = self.__executor.submit(client.setup, deepcopy(game_state), player.get_goal_position())
            future_list.append(future)
        responses = gather_protected(future_list, timeout_seconds=self.__timeout_seconds)
        self.__handle_broadcast_acknowledgements(responses, game_state)

    def __generate_players(self, board: Board, count: int) -> List[Player]:
        """
        Generates the initial info (home, goal, current, color) for a given number of players on a given board
        :param board: The Board to prepare players for
        :param count: The number of player information pieces to create
        :return: A list of Player instances with unique homes
        """
        players: List[Player] = []
        homes: Set[Position] = set()
        for idx in range(count):
            # Make a unique color
            color = ALL_NAMED_COLORS[idx] if idx < len(ALL_NAMED_COLORS) else str(idx).zfill(6)
            player = Player.from_home_goal_color(self.__generate_unique_home(board, homes),
                                                 self.__generate_goal(board),
                                                 color)
            players.append(player)
            homes.add(player.get_home_position())
        return players

    @staticmethod
    def __generate_unique_home(board: Board, prohibited_homes: Set[Position]) -> Position:
        """
        Method to generate a unique home Position for a player in the game
        :param board: The Board on which the player's home should be placed
        :param prohibited_homes: A Set of Positions which are already taken as home positions of other players
        :return: A Position representing the unique home Position for a player to use
        :raises: ValueError if there are no unique home tiles remaining, it is the job of whoever creates the referee
        to only permit the maximum number of players to avoid this error being raised.
        TODO: Test this
        """
        for row in range(board.get_height()):
            for col in range(board.get_width()):
                if board.check_stationary_position(row, col):
                    potential_position = Position(row, col)
                    if potential_position not in prohibited_homes:
                        return potential_position
        raise ValueError("No Unique Homes Left")

    @staticmethod
    def __generate_goal(board: Board) -> Position:
        """
        Method to generate a goal Position for a player in the game
        :param board: The Board on which the player's goal should be placed
        :return: A Position representing the goal Position for a player to use
        """
        for row in range(board.get_height()):
            for col in range(board.get_width()):
                if board.check_stationary_position(row, col):
                    return Position(row, col)
        raise ValueError("Board did not have any stationary positions")

    def __inform_winning_players(self, game_state: State) -> None:
        """
        Tells all winning players they have won the game
        :return: None
        """
        winning_players = game_state.get_closest_players_to_victory()
        future_list: "List[Future[Any]]" = []
        for client, player in zip(self.__current_players, game_state.get_players()):
            did_win = player in winning_players
            future = self.__executor.submit(client.win, did_win)
            future_list.append(future)
        responses = gather_protected(future_list, timeout_seconds=self.__timeout_seconds)
        # clients that fail to acknowledge will be moved from current players to cheater players by this method
        # clients which are still in current_players are the only candidates for the GameOutcome winners
        self.__handle_broadcast_acknowledgements(responses, game_state)
        self.__winning_players = [client for client, player in zip(self.__current_players, game_state.get_players())
                                  if player in winning_players]

    def __is_valid_move(self, proposed_move: Move, game_state: State) -> bool:
        """
        A method to validate the proposed move is a valid rotation, valid slide and insert, and valid player move
        :param proposed_move: The proposed Move to perform
        :return: True if the move is valid, False otherwise
        """
        return self.__check_rotation(proposed_move.get_spare_tile_rotation_degrees()) \
               and self.__check_slide_and_insert(proposed_move.get_slide_index(),
                                                 proposed_move.get_slide_direction(), game_state) \
               and self.__check_player_move(proposed_move, game_state)

    @staticmethod
    def __check_rotation(rotation_degrees: int) -> bool:
        """
        A method to validate the rotation of the spare Tile is a multiple of 90 degrees
        :param rotation_degrees: the suggested rotation for the spare Tile
        :return: True if the rotation is a multiple of 90, False otherwise
        """
        return rotation_degrees % 90 == 0

    @staticmethod
    def __check_slide_and_insert(slide_index: int, slide_direction: Direction, game_state: State) -> bool:
        """
        A method to validate the slide is a slideable row and not undoing the previous slide
        :param slide_index: The suggested index to slide on
        :param slide_direction: The suggested Direction to slide in
        :return: True if the suggest slide and insert is valid, False if not
        """
        previous_moves = game_state.get_all_previous_non_passes()
        if previous_moves:
            last_index, last_direction = previous_moves[-1]
            if last_index == slide_index and last_direction == slide_direction.get_opposite_direction():
                return False
        if slide_direction is Direction.UP or slide_direction is Direction.DOWN:
            return game_state.get_board().can_slide_vertically(slide_index)
        return game_state.get_board().can_slide_horizontally(slide_index)

    @staticmethod
    def __check_player_move(proposed_move: Move, game_state: State) -> bool:
        """
        A method to check the player move is to a tile that is on the Board and to a destination they can reach after
        sliding and inserting
        :param proposed_move: The proposed rotation, slide, and player move
        :return: True if the player move is valid, False otherwise
        """
        state_copy = deepcopy(game_state)
        state_copy.rotate_spare_tile(proposed_move.get_spare_tile_rotation_degrees())
        state_copy.slide_and_insert(proposed_move.get_slide_index(), proposed_move.get_slide_direction())
        return state_copy.can_active_player_reach_position(proposed_move.get_destination_position())

    def __perform_pass(self) -> None:
        """
        A helper method to perform a Pass move
        :return: None
        """

    def __run_round(self, game_state: State) -> bool:
        """
        Runs a round of a game. A round is considered complete when all players have taken a turn.
        :param game_state: represents the current state of the game
        :return: True if the game is over, otherwise False
        """
        any_player_moved = False
        num_players = len(self.__current_players)
        for _ in range(num_players):
            self.__did_active_player_cheat = False
            any_player_moved |= self.__run_active_player_turn(game_state)
            self.send_state_updates_to_observers(game_state)
            if not self.__current_players:
                return True
            if game_state.did_active_player_win():
                return True
            if not self.__did_active_player_cheat:
                game_state.change_active_player_turn()
        return not any_player_moved

    def __run_active_player_turn(self, game_state: State) -> bool:
        """
        Runs a single player turn within a game given the current game state
        :param game_state: represents the current state of the game
        :return: True if the player moves legally, otherwise False
        """
        player_index = game_state.get_active_player_index()
        client = self.__current_players[player_index]
        # TODO: remove other players' secret info
        response = await_protected(self.__executor.submit(lambda: client.take_turn(deepcopy(game_state))),
                                   timeout_seconds=self.__timeout_seconds)
        if not response.is_present:
            self.__handle_cheater(client, game_state)
            return False
        proposed_move = response.get_or_throw()
        proposed_move.perform_move_or_pass(lambda move: self.__perform_move(move, client, game_state),
                                           lambda _: self.__perform_pass())
        # TODO: Fix dynamic dispatch so we can validate moves here and remove use of isinstance
        return isinstance(proposed_move, Move) and not self.__did_active_player_cheat

    def send_state_updates_to_observers(self, game_state: State) -> None:
        """
        Updates all subscribed observers when a game of Labyrinth has a new state.
        Note: misbehaving observers are not kicked out of the list
        :return: None
        """
        future_list = [
            self.__executor.submit(observer.receive_new_state, deepcopy(game_state))
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
            self.__executor.submit(observer.set_game_is_over)
            for observer in self.__observers
        ]
        gather_protected(future_list, timeout_seconds=self.__timeout_seconds)
