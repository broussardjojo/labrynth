import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List, Tuple
from selectors import BaseSelector, DefaultSelector, EVENT_READ

import ijson
from pydantic import ValidationError

from ..Common.utils import Maybe, Nothing, Just, is_valid_player_name
from ..Players.api_player import APIPlayer
from ..Referee.referee import Referee
from ..Remote.messenger import Messenger
from ..Remote.player import RemotePlayer


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


class Server:
    """
    A class representing the server to run a game of Labyrinth
    """
    __messengers: Dict[Messenger, socket.socket]
    __pending_handshakes: Dict[Messenger, Tuple[float, Future, socket.socket]]
    __port_num: int
    __selector: BaseSelector
    __waiting_period: int
    HANDSHAKE_TIMEOUT_SECONDS = 2
    MAX_TO_START = 6
    WAITING_PERIOD_SECONDS = 20

    def __init__(self, port_num: int):
        """
        Constructor for a Server which will use the provided port_num to list for players
        :param port_num: an int representing the port that this server should expose to listen
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self.__messengers = {}
        self.__pending_handshakes = {}
        self.__selector = DefaultSelector()
        self.__waiting_period = 0
        if 0 < port_num < 65536:
            self.__port_num = port_num
        else:
            raise ValueError("Invalid port number supplied")

    def conduct_game(self) -> Tuple[List[str], List[str]]:
        """
        Create a TCP socket to listen and register players then run a game of Labyrinth with all
        successfully registered players
        :return: Two lists of strings representing the names of the winning and cheating players
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            socket_server.bind(("0.0.0.0", self.__port_num))
            # listen takes a `backlog` argument for the number of unaccepted connections the server can have, anything
            # beyond that is refused.
            socket_server.listen(8)
            self.__selector.register(socket_server, EVENT_READ)
            start_time = time.time()
            with ThreadPoolExecutor() as executor:
                while True:
                    new_clients = self.__accept_connections(socket_server)
                    for messenger, tcp_connection in new_clients:
                        future = executor.submit(self.__handshake, messenger)
                        self.__pending_handshakes[messenger] = time.time(), future, tcp_connection
                    self.__handle_handshake_timeouts()
                    elapsed_time = time.time() - start_time
                    maybe_players = self.__get_players_if_enough_players(elapsed_time)
                    # TODO: close all connections on game end
                    if maybe_players.is_present:
                        referee = Referee()
                        winners, cheaters = referee.run_game(maybe_players.get())
                        winners_names = [player.name() for player in winners]
                        cheaters_names = [player.name() for player in cheaters]
                        return winners_names, cheaters_names
                    if self.__waiting_period >= 2:
                        return [], []

    @staticmethod
    def __handshake(messenger: Messenger) -> str:
        """
        Perform a handshake with the messenger to receive their name
        :param messenger: A Messenger representing the client to handshake with
        :return: A string representing the name supplied by the player
        :raises: InvalidNameError if the name provided doesn't conform to constraints listed on the spec:
        A Name is a string of at least one and at most 20 alpha-numeric characters,
         i.e., it also matches the regular expression "^[a-zA-Z0-9]+$"
        """
        name = messenger.call("name", ())
        if not is_valid_player_name(name):
            raise InvalidNameError("Invalid name")
        return name

    def __accept_connections(self, socket_server: socket.socket) -> List[Tuple[Messenger, socket.socket]]:
        """
        Listens and accepts any incoming connections for 0.1 seconds
        :param socket_server: a socket representing the socket clients can connect to
        :return: a List of Messenger/socket pairs representing clients and their connections
        """
        ready = self.__selector.select(timeout=0.1)
        messenger_list: List[Tuple[Messenger, socket.socket]] = []
        for key, events in ready:
            if key.fileobj is socket_server:
                socket_client, _ = socket_server.accept()
                client_messenger = Messenger(socket_client.makefile("rb", buffering=0),
                                             socket_client.makefile("wb", buffering=0))
                messenger_list.append((client_messenger, socket_client))
        return messenger_list

    def __handle_handshake_timeouts(self) -> None:
        """
        A method to update the current set of pending handshakes. Messengers with successful handshakes are added to
        __messengers and messengers with timeouts or failed handshakes are closed and deleted from __pending_handshakes
        :return: None
        """
        current_time = time.time()
        # use list to allow us to modify the dict while looping over it
        for messenger, (start_time, future, connection) in list(self.__pending_handshakes.items()):
            handshake_outcome: Maybe[bool] = Nothing()
            if future.done():
                try:
                    future.result()
                    handshake_outcome = Just(True)
                    print("handshake complete", file=sys.stderr)
                except (ValidationError, ijson.IncompleteJSONError, InvalidNameError) as e:
                    print("kicking out player ", e, file=sys.stderr)
                    handshake_outcome = Just(False)
            elif current_time - start_time >= self.HANDSHAKE_TIMEOUT_SECONDS:
                print("kicking out player: timeout", file=sys.stderr)
                handshake_outcome = Just(False)
            if handshake_outcome.is_present:
                self.__pending_handshakes.pop(messenger)
                if not handshake_outcome.get():
                    self.__shutdown_if_needed(connection)
                else:
                    self.__messengers[messenger] = connection

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
        if len(self.__messengers) >= min_to_start:
            items = list(self.__messengers.items())
            for messenger, connection in items[self.MAX_TO_START:]:
                self.__messengers.pop(messenger)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
            return Just([RemotePlayer(messenger) for messenger, _ in items[:self.MAX_TO_START]])
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
