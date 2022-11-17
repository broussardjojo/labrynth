import contextlib
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from selectors import BaseSelector, DefaultSelector, EVENT_READ
from typing import Dict, List, Tuple

import ijson
from pydantic import ValidationError, StrictStr, parse_obj_as

from ..Common.utils import Maybe, Nothing, Just, is_valid_player_name
from ..Players.api_player import APIPlayer
from ..Referee.observer import Observer
from ..Referee.referee import Referee
from ..Remote.player import RemotePlayer


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


class Server:
    """
    A class representing the server to run a game of Labyrinth
    """
    __players: Dict[RemotePlayer, socket.socket]
    __pending_handshakes: "Dict[Future[str], Tuple[float, socket.socket]]"
    __port_num: int
    __selector: BaseSelector
    __waiting_period: int
    HANDSHAKE_TIMEOUT_SECONDS = 2
    MAX_TO_START = 6
    WAITING_PERIOD_SECONDS = 5

    def __init__(self, port_num: int):
        """
        Constructor for a Server which will use the provided port_num to listen for players
        :param port_num: an int representing the port that this server should expose to listen
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self.__players = {}
        self.__pending_handshakes = {}
        self.__selector = DefaultSelector()
        self.__waiting_period = 0
        if 0 < port_num < 65536:
            self.__port_num = port_num
        else:
            raise ValueError("Invalid port number supplied")

    @contextlib.contextmanager
    def __bind(self) -> socket.socket:
        """
        Binds a server socket to the configured port number, yields control to the main server logic block,
        then shuts down any connections that are still open
        :return: None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            try:
                socket_server.bind(("0.0.0.0", self.__port_num))
                # listen takes a `backlog` argument for the number of unaccepted connections the server can have,
                # anything beyond that is refused.
                socket_server.listen(8)
                yield socket_server
            finally:
                players = list(self.__players.keys())
                for player in players:
                    conn = self.__players.pop(player)
                    self.__shutdown_if_needed(conn)
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
        with self.__bind() as socket_server:
            self.__selector.register(socket_server, EVENT_READ)
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=32) as executor:
                while True:
                    new_clients = self.__accept_connections(socket_server)
                    for tcp_connection in new_clients:
                        future = executor.submit(self.__handshake, tcp_connection)
                        self.__pending_handshakes[future] = time.time(), tcp_connection
                    self.__handle_handshake_timeouts()
                    elapsed_time = time.time() - start_time
                    maybe_players = self.__get_players_if_enough_players(elapsed_time)
                    # TODO: close all connections on game end
                    if maybe_players.is_present:
                        referee = Referee(executor=executor)
                        winners, cheaters = referee.run_game(maybe_players.get())
                        winners_names = [player.name() for player in winners]
                        cheaters_names = [player.name() for player in cheaters]
                        return winners_names, cheaters_names
                    if self.__waiting_period >= 2:
                        return [], []

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
        return connection_list

    def __handle_handshake_timeouts(self) -> None:
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
                    remote_player = RemotePlayer.from_socket(future.result(), connection)
                    self.__players[remote_player] = connection
                    print("handshake complete, name={}".format(name), file=sys.stderr)
                except (ValidationError, ijson.IncompleteJSONError, InvalidNameError) as exc:
                    self.__shutdown_if_needed(connection)
                    print("handshake failed, exception={}".format(exc), file=sys.stderr)
            elif current_time - start_time >= self.HANDSHAKE_TIMEOUT_SECONDS:
                self.__pending_handshakes.pop(future)
                self.__shutdown_if_needed(connection)
                print("handshake timed out", file=sys.stderr)

    def __get_players_if_enough_players(self, elapsed_time: float) -> Maybe[List[APIPlayer]]:
        """
        Method to get the list of APIPlayers if there are enough registered at the given time
        :param elapsed_time: a float representing the amount of time that has passed since the waiting periods began
        :return: a List of APIPlayers if there are enough players to start a game, a Nothing if there aren't
        side effect: Mutates __waiting_period
        """
        min_to_start = 6
        new_waiting_period = int(elapsed_time // self.WAITING_PERIOD_SECONDS)
        if new_waiting_period > self.__waiting_period:
            self.__waiting_period = new_waiting_period
            min_to_start = 2
        if len(self.__players) >= min_to_start:
            # noinspection PyTypeChecker
            items: List[Tuple[RemotePlayer, socket.socket]] = list(self.__players.items())
            for messenger, connection in items[self.MAX_TO_START:]:
                self.__players.pop(messenger)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
            return Just([player for player, _ in items[:self.MAX_TO_START]])
        return Nothing()

    @staticmethod
    def __shutdown_if_needed(connection: socket.socket) -> None:
        """
        A method to shut down the given socket if it is not already closed
        :param connection: a socket representing the desired socket to close
        :return: None
        """
        try:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        except OSError:
            pass


if __name__ == '__main__':
    server = Server(9999)
    print(server.conduct_game())
