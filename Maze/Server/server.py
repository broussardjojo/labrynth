import contextlib
import logging
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from selectors import BaseSelector, DefaultSelector, EVENT_READ
from typing import Dict, List, Tuple, Iterator, Callable, Union, IO

import ijson
from pydantic import ValidationError, StrictStr, parse_obj_as
from typing_extensions import assert_never

from Maze.Common.utils import Maybe, Nothing, Just, is_valid_player_name
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Referee.referee import Referee, GameOutcome
from Maze.Remote.types import IOBytes
from Maze.Remote.player import RemotePlayer
from Maze.Remote.readable_stream_wrapper import ReadableStreamWrapper
from Maze.Remote.safe_remote_player import SafeRemotePlayer
from Maze.Server.signup_state import TimingEvent, CompletedHandshakeEvent, SignupState, RunGamePhase, \
    WaitingPeriodPhase, CancelledPhase
from Maze.config import CONFIG

log = logging.getLogger(__name__)


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


# A run game function takes in a Referee and list of safe players, and
# returns a GameOutcome (winners: List[APIPlayer], cheaters: List[APIPlayer]
RunGameFn = Callable[[Referee, List[SafeAPIPlayer]], GameOutcome]


class Server:
    """
    A class representing the server to run a game of Labyrinth
    """
    _state: SignupState
    _pending_handshakes: "List[Tuple[Future[str], float, socket.socket]]"
    _port_num: int
    _selector: BaseSelector
    _run_game_function: RunGameFn

    def __init__(self, port_num: int,
                 run_game_function: RunGameFn = Referee.run_game_with_safe_players):
        """
        Constructor for a Server which will use the provided port_num to listen for players
        :param port_num: an int representing the port that this server should expose to listen
        :param run_game_function: A callable to run the game; this allows for custom starting states and other
            configurations.
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self._state = SignupState(phase=WaitingPeriodPhase(0), players=[])
        self._pending_handshakes = []
        self._selector = DefaultSelector()
        if 0 < port_num < 65536:
            self._port_num = port_num
        else:
            raise ValueError("Invalid port number supplied")
        self._run_game_function = run_game_function

    @contextlib.contextmanager
    def __bind(self) -> Iterator[socket.socket]:
        """
        Binds a server socket to the configured port number, yields control to the main server logic block,
        then shuts down any connections that are still open
        :return: an Iterator[socket.socket] intended to be used in a `with` block
        side effect: registers the EVENT_READ of the server socket with self.__selector
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            try:
                # Allow the server to reuse an address within the OS's TIME_WAIT after the previous connection on it
                # is closed, aids with testing
                socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socket_server.bind(("0.0.0.0", self._port_num))
                # listen takes a `backlog` argument for the number of unaccepted connections the server can have,
                # anything beyond that is refused.
                socket_server.listen(8)
                self._selector.register(socket_server, EVENT_READ)
                yield socket_server
            finally:
                for player in self._state.players:
                    player.on_kicked()
                for _, _, conn in self._pending_handshakes:
                    self._shutdown_if_needed(conn)
                self._state = SignupState(phase=WaitingPeriodPhase(0), players=[])
                self._pending_handshakes = []

    def conduct_game(self) -> Tuple[List[str], List[str]]:
        """
        Create a TCP socket to listen and register players then run a game of Labyrinth with all
        successfully registered players
        :return: Two lists of strings representing the names of the winning and cheating players
        """
        with ThreadPoolExecutor(max_workers=32) as executor:
            with self.__bind() as socket_server:
                self.accept_players(socket_server, executor)
                if isinstance(self._state.phase, RunGamePhase):
                    # These players come in Oldest -> Youngest order, which is the opposite order from what the Referee
                    # expects. As a result, we reverse the list that SignupState accumulated.
                    ordered_players = self._state.players[::-1]
                    winners, cheaters = self._run_game(ordered_players, executor)
                    winners_names = [player.name() for player in winners]
                    cheaters_names = [player.name() for player in cheaters]
                    return winners_names, cheaters_names
                elif isinstance(self._state.phase, CancelledPhase):
                    return [], []
                elif isinstance(self._state.phase, WaitingPeriodPhase):
                    raise ValueError("Invalid returned state from accept_players")
                else:
                    assert_never(self._state.phase)

    def accept_players(self, socket_server: socket.socket, executor: ThreadPoolExecutor) -> None:
        """
        Accepts players by listening on socket and runs handshakes until the game is ready to start or has waited for
         two waiting periods
        :param socket_server: a socket representing the server which is listening for connections
        :param executor: a ThreadPoolExecutor to spawn handshake threads from
        :return: None
        Side effect: Updates __state. The state must not be in WaitingPeriodPhase when this method returns
        """
        start_time = time.time()
        while isinstance(self._state.phase, WaitingPeriodPhase):
            new_clients = self._accept_connections(socket_server)
            for tcp_connection in new_clients:
                # The handshake method works with a readable stream of bytes rather than a socket, for
                # easier testing. However, it is not reused, because there could be thread safety issues.
                handshake_channel = tcp_connection.makefile("rb", buffering=0)
                future = executor.submit(self.handshake, handshake_channel)
                self._pending_handshakes.append((future, time.time(), tcp_connection))
            for remote_player in self._handle_handshake_timeouts(executor):
                # Try to add the players who've successfully handshaken to the game
                # It might just ignore the player, in which we need to tell it to close its connection explicitly
                # Otherwise, it will be closed by a Referee call to on_kicked OR the Server.__bind above
                self._state = self.update_signup_state(self._state, CompletedHandshakeEvent(remote_player))
                if remote_player not in self._state.players:
                    remote_player.on_kicked()
            elapsed_time = time.time() - start_time
            self._state = self.update_signup_state(self._state, TimingEvent(elapsed_time))

    @staticmethod
    def handshake(binary_read_channel: IOBytes) -> str:
        """
        Perform a handshake with the client on the given read channel to receive their name
        :param binary_read_channel: A file-like object from which bytes can be read
        :return: A string representing the name supplied by the player
        :raises: InvalidNameError if the name provided doesn't conform to constraints listed on the spec:
        A Name is a string of at least one and at most 20 alpha-numeric characters,
         i.e., it also matches the regular expression "^[a-zA-Z0-9]+$"
        """
        # temporarily open a file interface to the socket. closing it doesn't close the actual connection
        read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
        json_name = next(read_channel)
        name = parse_obj_as(StrictStr, json_name)
        if not is_valid_player_name(name):
            raise InvalidNameError("Invalid name")
        return name

    def _accept_connections(self, socket_server: socket.socket) -> List[socket.socket]:
        """
        Listens and accepts any incoming connections for 0.1 seconds
        :param socket_server: a socket representing the socket clients can connect to
        :return: a List of sockets representing new client connections
        """
        ready = self._selector.select(timeout=0.1)
        connection_list: List[socket.socket] = []
        for key, _events in ready:
            if key.fileobj is socket_server:
                socket_client, _ = socket_server.accept()
                connection_list.append(socket_client)
                log.info("Accepted %s", socket_client.getpeername())
        return connection_list

    def _handle_handshake_timeouts(self, executor: ThreadPoolExecutor) -> Iterator[SafeAPIPlayer]:
        """
        A method to update the current set of pending handshakes. Clients with successful handshakes are returned, and
        clients with timeouts or failed handshakes are closed and deleted from __pending_handshakes
        :returns: an Iterator which will supply the SafeAPIPlayer for each successful handshake
        Side effect: modifies __pending_handshakes
        """
        current_time = time.time()

        # Filter the list into the 2 cases we can deal with now, and the 1 case that we can't
        timed_out_handshakes: "List[Tuple[Future[str], float, socket.socket]]" = []
        settled_handshakes: "List[Tuple[Future[str], float, socket.socket]]" = []
        pending_handshakes: "List[Tuple[Future[str], float, socket.socket]]" = []
        for future, start_time, connection in self._pending_handshakes:
            if future.done():
                settled_handshakes.append((future, start_time, connection))
            elif current_time - start_time >= CONFIG.server_handshake_timeout:
                timed_out_handshakes.append((future, start_time, connection))
            else:
                pending_handshakes.append((future, start_time, connection))
        self._pending_handshakes = pending_handshakes

        # Clean up resources for clients who did not attempt to handshake in time
        for _, _, connection in timed_out_handshakes:
            self._handle_timed_out_handshake(connection)

        # For clients who have attempted a handshake, determine if they were successful
        # If they were, yield the remote player; otherwise, clean up resources
        for future, _, connection in settled_handshakes:
            try:
                name = future.result()
                yield SafeRemotePlayer.from_socket(name, executor, connection)
                log.info("handshake complete, name=%s", name)
            except (ijson.IncompleteJSONError, ValidationError, InvalidNameError) as exc:
                # catch the errors that future.result() can raise; handshake could have gotten malformed JSON,
                # the wrong type of JSON, or a JSON string which isn't a valid name
                self._handle_invalid_handshake(connection, exc)

    def _handle_timed_out_handshake(self, connection: socket.socket) -> None:
        """
        Handles a timed out handshake. At minimum, this method should shut down the connection.
        :param connection: A socket.socket
        :return: None
        """
        self._shutdown_if_needed(connection)
        log.info("handshake timed out")

    def _handle_invalid_handshake(self, connection: socket.socket, exception: Exception) -> None:
        """
        Handles a handshake in which the client misbehaved. At minimum, this method should shut down the connection.
        :param connection: A socket.socket
        :return: None
        """
        self._shutdown_if_needed(connection)
        log.info("handshake failed", exc_info=exception)

    @staticmethod
    def update_signup_state(current_state: SignupState,
                            action: Union[TimingEvent, CompletedHandshakeEvent]) -> SignupState:
        if isinstance(action, TimingEvent):
            return Server._update_for_timing(current_state, action)
        elif isinstance(action, CompletedHandshakeEvent):
            return Server._update_for_completed_handshake(current_state, action)
        else:
            assert_never(action)

    @staticmethod
    def _update_for_timing(current_state: SignupState, action: TimingEvent) -> SignupState:
        if isinstance(current_state.phase, (CancelledPhase, RunGamePhase)):
            # Nothing needs to change in the signup state once the game is cancelled or running
            return current_state
        elif isinstance(current_state.phase, WaitingPeriodPhase):
            next_waiting_period = int(action.elapsed // CONFIG.server_waiting_period_seconds)
            if next_waiting_period > current_state.phase.period_num:
                if len(current_state.players) >= CONFIG.server_minimum_players_to_start:
                    # Start game if we have >= min_players
                    return SignupState(phase=RunGamePhase(), players=current_state.players)
                elif next_waiting_period >= CONFIG.server_number_of_waiting_periods:
                    # Cancel game if we have < min_players, and the server has already run its last waiting period
                    return SignupState(phase=CancelledPhase(), players=current_state.players)
                else:
                    return SignupState(phase=WaitingPeriodPhase(next_waiting_period), players=current_state.players)

            elif next_waiting_period == current_state.phase.period_num:
                # No change in waiting period
                return current_state

            else:
                # Time traveler
                raise ValueError("The timing events sent to a Server must be monotonically increasing")
        else:
            assert_never(current_state.phase)

    @staticmethod
    def _update_for_completed_handshake(current_state: SignupState, action: CompletedHandshakeEvent) -> SignupState:
        if isinstance(current_state.phase, (CancelledPhase, RunGamePhase)):
            # Nothing needs to change in the signup state once the game is cancelled or running
            return current_state
        elif isinstance(current_state.phase, WaitingPeriodPhase):
            next_players = [*current_state.players, action.player]
            if len(next_players) < CONFIG.server_maximum_players_to_start:
                # Continue waiting if we have < max_players
                return SignupState(phase=current_state.phase, players=next_players)

            elif len(next_players) == CONFIG.server_maximum_players_to_start:
                # Start game immediately if we have exactly max_players
                return SignupState(phase=RunGamePhase(), players=next_players)

            else:
                # Should never happen
                raise ValueError("Invalid state. Phase is WaitingPeriod, but already had at least "
                                 f"{CONFIG.server_maximum_players_to_start} players.")
        else:
            assert_never(current_state.phase)

    @staticmethod
    def _shutdown_if_needed(connection: socket.socket) -> None:
        """
        A method to shut down the given socket if it is not already closed
        :param connection: a socket representing the desired socket to close
        :return: None
        """
        log.info("Closing %s", connection.getpeername())
        try:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
            log.info("Closing success")
        except OSError:
            log.error("Closing failed", exc_info=True)

    def _run_game(self, players: List[SafeAPIPlayer], executor: ThreadPoolExecutor) -> GameOutcome:
        """
        Run a game of Labyrinth with the given list of players and executor
        :param players: a List of APIPlayers representing the players to play in the game
        :param executor: a ThreadPoolExecutor for the referee to spawn threads from
        :return: The winners names followed by the cheaters names
        """
        referee = Referee(executor=executor)
        return self._run_game_function(referee, players)
