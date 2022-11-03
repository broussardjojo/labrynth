from threading import Thread
from typing import List, Union
import signal
from copy import deepcopy
from ..Players.player import Player
from ..Common.direction import Direction
from ..Common.state import State
from ..Common.board import Board
from ..Common.observableState import ObservableState
from ..Common.position import Position
from ..Common.utils import get_opposite_direction
from ..Players.move import Move, Pass
from multipledispatch import dispatch
from .observer import Observer


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
    def __init__(self, has_observer: bool = False):
        """
        Creates an instance of a Referee given a game State
        """
        self.__has_observer = has_observer
        if self.__has_observer:
            self.__observer = Observer()
        self.__reset_referee()

    def __reset_referee(self):
        self.__cheater_players = []
        self.__winning_players = []
        self.__num_rounds = 0
        self.__all_player_goals = []
        self.__passed_players = []
        self.__did_last_player_cheat = False

    @staticmethod
    def get_proposed_board(list_of_players: List[Player]) -> Board:
        """
        Gets a Board from Players' proposals
        NOTE: this method is mainly defined for testing at this point, we will implement it fully when it is required
        :param list_of_players: the list of Players allowed to propose a Board
        :return: a randomly selected Board from the list of proposed Boards
        """
        return Board.from_random_board(seed=3)

    def __perform_valid_move(self, proposed_move: Move, active_player: Player, game_state: State) -> None:
        """
        Perform a validated move by rotating, sliding and inserting, and moving. Also resets the list of passed Players
        because this player is not passing.
        :param proposed_move: The Move to make
        :param active_player: The active Player who is making this Move
        :return: None
        """
        self.__passed_players = []
        game_state.rotate_spare_tile(proposed_move.get_spare_tile_rotation_degrees())
        game_state.slide_and_insert(proposed_move.get_slide_index(),
                                    proposed_move.get_slide_direction())
        game_state.move_active_player_to(proposed_move.get_destination_position())
        if game_state.is_active_player_at_goal():
            active_player.setup(active_player.get_home_position())

    def __perform_move(self, proposed_move: Move, active_player: Player, game_state: State) -> None:
        """
        Validates the proposed Move by the active Player. If the move is valid, perform the move, otherwise, kick out
        the active player. If the player passes, add them to the list of passing players
        :param proposed_move: a Move representing the proposed Move to make
        :param active_player: a Player representing the active player to make this Move
        :return: None
        """
        if self.__is_valid_move(proposed_move, game_state):
            self.__perform_valid_move(proposed_move, active_player, game_state)
        else:
            self.__handle_cheater(active_player, game_state)

    def __handle_cheater(self, active_player: Player, game_state: State) -> None:
        """
        Kicks the given player out of the game and adds them to a list of cheating players.
        :param active_player: the player found cheating
        :return: None
        side effect: mutates the cheater_players list, mutates the game_state by kicking out the active player
        """
        game_state.kick_out_active_player()
        self.__cheater_players.append(active_player)
        self.__did_last_player_cheat = True

    def __handle_timeout(self, active_player: Player, game_state: State) -> None:
        """
        Raises an error given that the active player takes to long to make their move and handles the active player as
        a cheater by kicking them out of the game and adding them to a list of cheating players.
        :param active_player: the player taking too long to move
        :return: None
        raises: TimeoutError
        """
        self.__handle_cheater(active_player, game_state)
        raise TimeoutError("Error: Player took to long to make their move")

    def __get_proposed_move(self, active_player: Player, game_state: State) -> Union[Move, Pass]:
        """
        Gets the proposed move from the active player. If the active player takes too long to communicate their desired
        move, then the game times them out and that player is removed from the game and added to a list of cheating
        players.
        :param active_player: the player who is proposing a move
        :return: a desired Move from the active player
        """
        # TODO: Replace whole method with APIPlayer central control for timeouts and pick new library
        observable_state = ObservableState(game_state.get_board())
        # signal.signal(signal.SIGALRM, lambda *_: self.__handle_timeout(active_player, game_state))
        # signal.alarm(10)
        proposed_move = active_player.take_turn(observable_state)
        # signal.alarm(0)
        return proposed_move

    @dispatch([Player])
    def run_game(self, players: List[Player]) -> (List[Player], List[Player]):
        """
        Entry method that runs a game of Labyrinth when given a list of players. It creates a State from the given list
        of players, sets up the game, and then runs the game.
        :param players: the list of players for a game of Labyrinth
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating.
        """
        self.__reset_referee()
        selected_board = self.get_proposed_board(players)
        game_state = State.from_board_and_players(selected_board, players)
        self.__setup(game_state)
        return self.__run_game_helper(game_state)

    @dispatch(State)
    def run_game(self, game_state: State) -> (List[Player], List[Player]):
        """
        Entry method that runs a game of Labyrinth when given a game state. It sets up and then runs the game.
        :param game_state: the state for a game of Labyrinth
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating.
        """
        self.__reset_referee()
        if self.__has_observer:
            thread = Thread(target=self.__run_game_helper, args=(game_state,))
            thread.start()
            self.__observer.display_gui()
            thread.join()
            return self.__winning_players, self.__cheater_players
        else:
            return self.__run_game_helper(game_state)

    def __run_game_helper(self, game_state: State) -> (List[Player], List[Player]):
        """
        Method to run a game of Labyrinth, this method will run until the game is over, for each player in the list
        it will request a move, validate the move, perform the move or kick the player out, and check if the game is
        over. At the end, the referee will inform all winning Players that they have won and return a list of winning
        Players and a List of cheating Players
        :return: A List of winning Players representing either the winner or all players who tied for the win and
        a List of cheating Players representing all Players who were kicked out for cheating.
        """
        if self.__has_observer:
            self.__observer.receive_new_state(game_state)
        while True:
            self.__did_last_player_cheat = False
            active_player_index = game_state.get_active_player_index()
            if active_player_index == len(game_state.get_players()) - 1:
                self.__num_rounds += 1
            active_player = game_state.get_players()[active_player_index]
            try:
                proposed_move = self.__get_proposed_move(active_player, game_state)
            except TimeoutError:
                if self.__game_not_over(game_state):
                    continue
                break
            proposed_move.perform_move_or_pass(lambda: self.__perform_move(proposed_move, active_player, game_state),
                                               lambda: self.__perform_pass(active_player))
            if self.__has_observer:
                self.__observer.receive_new_state(game_state)
            if self.__game_not_over(game_state):
                continue
            break
        self.__inform_winning_players()
        return self.__winning_players, self.__cheater_players

    def __setup(self, game_state: State) -> None:
        """
        Method to setup the board and give each player their goal Tile
        :return: None
        """
        for player in game_state.get_players():
            observable_state = ObservableState(deepcopy(game_state.get_board()))
            player.setup(observable_state, self.__generate_unique_goal(game_state))

    def __generate_unique_goal(self, game_state: State) -> Position:
        """
        Method to generate a unique goal Position for a Player in the game
        :return: A Position representing the unique goal Position for a player to use
        :raises: ValueError if there are no unique goal tiles remaining, it is the job of whoever creates the referee
        to only permit the maximum number of players to avoid this error being raised.
        """
        tile_grid = game_state.get_board().get_tile_grid()
        for row in range(len(tile_grid)):
            for col in range(len(tile_grid[row])):
                if game_state.get_board().check_stationary_position(row, col):
                    potential_position = Position(row, col)
                    if potential_position not in self.__all_player_goals:
                        self.__all_player_goals.append(potential_position)
                        return potential_position
        raise ValueError("No Unique Goals Left")

    def __game_not_over(self, game_state: State) -> bool:
        """
        Returns whether the game is over or not. The game is considered over if the active player reaches their home
        position after visiting their goal position, the number of rounds reaches 1000, every player in a round
        passes, or there are 0 players left in the game.
        :return: True if the game is over, otherwise False
        """
        if len(game_state.get_players()) == 0:
            if self.__has_observer:
                self.__observer.game_is_over()
            return False
        active_player = game_state.get_players()[game_state.get_active_player_index()]
        if game_state.is_active_player_at_home() and game_state.active_player_has_reached_goal():
            self.__winning_players = [active_player]
            if self.__has_observer:
                self.__observer.game_is_over()
            return False
        if self.__num_rounds == 1000 or len(self.__passed_players) == len(game_state.get_players()):
            self.__winning_players = game_state.get_closest_players_to_victory()
            if self.__has_observer:
                self.__observer.game_is_over()
            return False
        if not self.__did_last_player_cheat:
            game_state.change_active_player_turn()
        return True

    def __inform_winning_players(self) -> None:
        """
        Tells all winning players they have won the game
        :return: None
        """
        for player in self.__winning_players:
            player.won(True)

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
            if last_index == slide_index and last_direction == get_opposite_direction(slide_direction):
                return False
        return game_state.get_board().can_slide(slide_index)

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
        board_copy = state_copy.get_board()
        try:
            destination_tile = board_copy.get_tile_by_position(proposed_move.get_destination_position())
        except ValueError:
            return False
        return state_copy.can_active_player_reach_given_tile(destination_tile)

    def __perform_pass(self, active_player) -> None:
        """
        A helper method to perform a Pass move
        :param active_player: The currently active player who is passing their turn
        :return: None
        """
        self.__passed_players.append(active_player)
