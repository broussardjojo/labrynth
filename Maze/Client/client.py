import json
import socket
import time
from types import TracebackType
from typing import Optional, Type

import ijson

from Maze.Players.api_player import APIPlayer
from Maze.Remote.referee import DispatchingReceiver

# The number of seconds that the client should wait before shutting down if it starts before the Server has.
WAIT_FOR_SERVER_DURATION = 15


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


def create_connection(host: str, port: int, retry_seconds: float = 0) -> socket.socket:
    """
    Yields a connection to the server. This method is responsible for retrying connection for up to
    a given number seconds before raising an error.
    :raises: socket.timeout if the final attempt in the allotted time period fails.
    :return: An iterator for a with block
    """
    delay_end = time.time() + retry_seconds
    delay_remaining: float = retry_seconds
    while delay_remaining >= 0:
        try:
            connection = socket.create_connection((host, port), timeout=min(delay_remaining, 1))
        except socket.timeout as error:
            delay_remaining = delay_end - time.time()
            if delay_remaining <= 0:
                raise error
        else:
            # Set infinite timeout; the client does not know how long the referee will take between
            # method calls, and shouldn't care
            connection.settimeout(None)
            # `yield` inside `with` adds the connection cleanup to the cleanup of our own `with self.connect`
            # block
            return connection
    raise RuntimeError("Timeout error failed to raise with no time remaining")


class Client:
    """
    A class representing the client to register for a game of Labyrinth. Usage should look like this:

        with Client(host, port) as client:
            player_service = client.register_for_game(LocalPlayer(...))
            player_service.listen_forever()
    """
    __connection: socket.socket

    def __init__(self, host_name: str, port_num: int):
        """
        Constructor for a Client which will connect to a game server at the provided port number
        :param host_name: a string representing the host that the client will connect to
        :param port_num: an int representing the port that the client will connect to
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        if not 0 < port_num < 65536:
            raise ValueError("Invalid port number supplied")
        self.__connection = create_connection(host_name, port_num, retry_seconds=WAIT_FOR_SERVER_DURATION)

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        try:
            self.__connection.close()
        except OSError:
            pass

    def register_for_game(self, player: APIPlayer) -> DispatchingReceiver:
        """
        Registers for the game being managed by the server connected to this client, then creates a
        DispatchingReceiver for it.
        :return: A DispatchingReceiver connected to the game
        """
        binary_read_channel = self.__connection.makefile("rb", buffering=0)
        read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
        write_channel = self.__connection.makefile("wb", buffering=0)
        write_channel.write(json.dumps(player.name()).encode("utf-8"))
        dispatcher = DispatchingReceiver(player, read_channel, write_channel)
        return dispatcher

