import contextlib
import logging
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from selectors import BaseSelector, DefaultSelector, EVENT_READ
from typing import Dict, List, Tuple, Iterator, Callable

import ijson
from pydantic import ValidationError, StrictStr, parse_obj_as

from Maze.Common.utils import Maybe, Nothing, Just, is_valid_player_name
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Referee.referee import Referee, GameOutcome
from Maze.Remote.player import RemotePlayer
from Maze.Remote.readable_stream_wrapper import ReadableStreamWrapper
from Maze.Remote.safe_remote_player import SafeRemotePlayer

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


@dataclass
class PlayerConnection:
    """
    Represents a Player across the network and its connection
    """
    safe_api_player: SafeAPIPlayer
    connection: socket.socket



# A run game function takes in a Referee and list of safe players, and
# returns a GameOutcome (winners: List[APIPlayer], cheaters: List[APIPlayer]
RunGameFn = Callable[[Referee, List[SafeAPIPlayer]], GameOutcome]


class Server:
    """
    A class representing the server to run a game of Labyrinth
    """
    __player_connections: Dict[socket.socket, PlayerConnection]
    __pending_handshakes: "Dict[Future[str], Tuple[float, socket.socket]]"
    __port_num: int
    __selector: BaseSelector
    __waiting_period: int
    __run_game_function: Callable[[Referee, List[SafeAPIPlayer]], GameOutcome]
    HANDSHAKE_TIMEOUT_SECONDS = 2
    MAX_TO_START = 6
    WAITING_PERIOD_SECONDS = 20

    def __init__(self, port_num: int,
                 run_game_function: RunGameFn = Referee.run_game_with_safe_players):
        """
        Constructor for a Server which will use the provided port_num to listen for players
        :param port_num: an int representing the port that this server should expose to listen
        :param run_game_function: A callable to run the game; this allows for custom starting states and other
            configurations.
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self.__player_connections = {}
        self.__pending_handshakes = {}
        self.__selector = DefaultSelector()
        self.__waiting_period = 0
        if 0 < port_num < 65536:
            self.__port_num = port_num
        else:
            raise ValueError("Invalid port number supplied")
        self.__run_game_function = run_game_function

    @contextlib.contextmanager
    def __bind(self) -> Iterator[socket.socket]:
        """
        Binds a server socket to the configured port number, yields control to the main server logic block,
        then shuts down any connections that are still open
        :return: None
        side effect: registers the EVENT_READ of the server socket with self.__selector
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            try:
                # Allow the server to reuse an address within the OS's TIME_WAIT after the previous connection on it
                # is closed, aids with testing
                socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                socket_server.bind(("0.0.0.0", self.__port_num))
                # listen takes a `backlog` argument for the number of unaccepted connections the server can have,
                # anything beyond that is refused.
                socket_server.listen(8)
                self.__selector.register(socket_server, EVENT_READ)
                yield socket_server
            finally:
                keys = list(self.__player_connections.keys())
                for key in keys:
                    player_conn = self.__player_connections.pop(key)
                    self.__shutdown_if_needed(player_conn.connection)
                future_list = list(self.__pending_handshakes.keys())
                for future in future_list:
                    _, conn = self.__pending_handshakes.pop(future)
                    self.__shutdown_if_needed(conn)

    def conduct_game(self) -> Tuple[List[str], List[str]]:
        """
        Create a TCP socket to listen and register players then run a game of Labyrinth with all
        successfully registered players
        :return: Two lists of strings representing the names of the winning and cheating players
        """
        with ThreadPoolExecutor(max_workers=32) as executor:
            with self.__bind() as socket_server:
                maybe_players = self.accept_players(socket_server, executor)
                if maybe_players.is_present:
                    winners, cheaters = self.__run_game(maybe_players.get(), executor)
                    winners_names = [player.name() for player in winners]
                    cheaters_names = [player.name() for player in cheaters]
                    return winners_names, cheaters_names
                else:
                    return [], []

    def accept_players(self, socket_server: socket.socket, executor: ThreadPoolExecutor) -> Maybe[List[SafeAPIPlayer]]:
        """
        Accepts players by listening on socket and runs handshakes until the game is ready to start or has waited for
         two waiting periods
        :param socket_server: a socket representing the server which is listening for connections
        :param executor: a ThreadPoolExecutor to spawn handshake threads from
        :return: a Just[List[APIPlayers]] if the game can begin, otherwise a Nothing
        """
        start_time = time.time()
        while not self.__waiting_period >= 2:
            new_clients = self.__accept_connections(socket_server)
            for tcp_connection in new_clients:
                future = executor.submit(self.__handshake, tcp_connection)
                self.__pending_handshakes[future] = time.time(), tcp_connection
            self.__handle_handshake_timeouts(executor)
            elapsed_time = time.time() - start_time
            maybe_players = self.__get_players_if_enough_players(elapsed_time)
            if maybe_players.is_present:
                return maybe_players
        return Nothing()

    @staticmethod
    def __handshake(connection: socket.socket) -> str:
        """
        Perform a handshake with the client on the given connection to receive their name
        :param connection: A socket.socket representing the client to handshake with
        :return: A string representing the name supplied by the player
        :raises: InvalidNameError if the name provided doesn't conform to constraints listed on the spec:
        A Name is a string of at least one and at most 20 alpha-numeric characters,
         i.e., it also matches the regular expression "^[a-zA-Z0-9]+$"
        """
        # temporarily open a file interface to the socket. closing it doesn't close the actual connection
        with connection.makefile("rb", buffering=0) as binary_read_channel:
            read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
            json_name = next(read_channel)
        name = parse_obj_as(StrictStr, json_name)
        if not is_valid_player_name(name):
            raise InvalidNameError("Invalid name")
        return name

    def __accept_connections(self, socket_server: socket.socket) -> List[socket.socket]:
        """
        Listens and accepts any incoming connections for 0.1 seconds
        :param socket_server: a socket representing the socket clients can connect to
        :return: a List of sockets representing new client connections
        """
        ready = self.__selector.select(timeout=0.1)
        connection_list: List[socket.socket] = []
        for key, _events in ready:
            if key.fileobj is socket_server:
                socket_client, _ = socket_server.accept()
                connection_list.append(socket_client)
                log.info("Opening %s", socket_client)
        return connection_list

    def __handle_handshake_timeouts(self, executor: ThreadPoolExecutor) -> None:
        """
        A method to update the current set of pending handshakes. Messengers with successful handshakes are added to
        __messengers and messengers with timeouts or failed handshakes are closed and deleted from __pending_handshakes
        :return: None
        """
        current_time = time.time()
        # use list to allow us to modify the dict while looping over it
        # mypy is fine with this but PyCharm has a bug where it thinks type(list(dict.items())) == List[Key] :(
        # noinspection PyTypeChecker
        items: "List[Tuple[Future[str], Tuple[float, socket.socket]]]" = list(self.__pending_handshakes.items())
        for future, (start_time, connection) in items:
            if future.done():
                self.__pending_handshakes.pop(future)
                try:
                    name = future.result()
                    raw_binary_read_channel = connection.makefile("rb", buffering=0)
                    binary_read_channel = ReadableStreamWrapper(raw_binary_read_channel)
                    read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
                    write_channel = connection.makefile("wb", buffering=0)
                    remote_player = RemotePlayer(name, read_channel, write_channel)
                    safe_remote_player = SafeRemotePlayer(remote_player, executor, binary_read_channel)
                    self.__player_connections[connection] = PlayerConnection(safe_remote_player, connection)
                    print("handshake complete, name={}".format(name), file=sys.stderr)
                except (ijson.IncompleteJSONError, ValidationError, InvalidNameError) as exc:
                    # catch the errors that future.result() can raise; handshake could have gotten malformed JSON,
                    # the wrong type of JSON, or a JSON string which isn't a valid name
                    self.__shutdown_if_needed(connection)
                    print("handshake failed, exception={}".format(exc), file=sys.stderr)
            elif current_time - start_time >= self.HANDSHAKE_TIMEOUT_SECONDS:
                self.__pending_handshakes.pop(future)
                self.__shutdown_if_needed(connection)
                print("handshake timed out", file=sys.stderr)

    def __get_players_if_enough_players(self, elapsed_time: float) -> Maybe[List[SafeAPIPlayer]]:
        """
        Method to get the list of APIPlayers if there are enough registered at the given time
        :param elapsed_time: a float representing the amount of time that has passed since the waiting periods began
        :return: a List of APIPlayers if there are enough players to start a game, a Nothing if there aren't
        side effect: Mutates __waiting_period
        """
        min_to_start = self.MAX_TO_START
        new_waiting_period = int(elapsed_time // self.WAITING_PERIOD_SECONDS)
        if new_waiting_period > self.__waiting_period:
            self.__waiting_period = new_waiting_period
            min_to_start = 2
        if len(self.__player_connections) >= min_to_start:
            # noinspection PyTypeChecker
            keys = list(self.__player_connections.keys())
            for key in keys[self.MAX_TO_START:]:
                player_conn = self.__player_connections.pop(key)
                self.__shutdown_if_needed(player_conn.connection)
            return Just([player_conn.safe_api_player for player_conn in self.__player_connections.values()])
        return Nothing()

    @staticmethod
    def __shutdown_if_needed(connection: socket.socket) -> None:
        """
        A method to shut down the given socket if it is not already closed
        :param connection: a socket representing the desired socket to close
        :return: None
        """
        log.info("Closing %s", connection)
        try:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
            log.info("Closing %s success", connection)
        except OSError:
            log.error("Closing %s failed", exc_info=True)

    def __run_game(self, players: List[SafeAPIPlayer], executor: ThreadPoolExecutor) -> GameOutcome:
        """
        Run a game of Labyrinth with the given list of players and executor
        :param players: a List of APIPlayers representing the players to play in the game
        :param executor: a ThreadPoolExecutor for the referee to spawn threads from
        :return: The winners names followed by the cheaters names
        """
        referee = Referee(executor=executor)
        return self.__run_game_function(referee, players)
