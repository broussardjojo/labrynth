import json
import logging
import socket
from types import TracebackType
from typing import Iterator, Any, IO, Tuple, Optional, Type

import ijson

from Maze.Common.thread_utils import sleep_interruptibly
from Maze.Players.api_player import APIPlayer
from Maze.Remote.readable_stream_wrapper import ReadableStreamWrapper
from Maze.Remote.referee import DispatchingReceiver
from Maze.config import CONFIG

log = logging.getLogger(__name__)


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


def create_connection(host: str, port: int) -> socket.socket:
    """
    Connects to the given host and port, retrying indefinitely until the connection succeeds.
    :return: A TCP connection
    """
    while True:
        log.info("Attempting to connect to %s:%s", host, port)
        try:
            connection = socket.create_connection((host, port))
        except OSError as exc:
            sleep_interruptibly(CONFIG.client_retry_sleep_duration)
            log.info("Retrying connection", exc_info=exc)
        else:
            # Set infinite timeout; the client does not know how long the referee will take between
            # method calls, and shouldn't care
            connection.settimeout(None)
            # `yield` inside `with` adds the connection cleanup to the cleanup of our own `with self.connect`
            # block
            return connection


class Client:
    """
    A class representing the client to register for a game of Labyrinth. Usage should look like this:

        with Client(host, port) as client:
            player_service = client.register_for_game(LocalPlayer(...))
            player_service.listen_forever()
    """
    __connection: socket.socket

    def __init__(self, connection: socket.socket):
        """
        Constructor for a Client which will connect to a game server at the provided port number
        :param host_name: a string representing the host that the client will connect to
        :param port_num: an int representing the port that the client will connect to
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self.__connection = connection
        log.info("Client connected")

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
        read_channel, write_channel = self._make_channels()
        return self._send_name(player, read_channel, write_channel)

    def _make_channels(self) -> Tuple[Iterator[Any], IO[bytes]]:
        """
        Creates a read channel (JSON values) and write channel (bytes) for the connection of this Client.
        :return: A tuple of the shape (Iterator[Any], IO[bytes])
        """
        raw_binary_read_channel = self.__connection.makefile("rb", buffering=0)
        binary_read_channel = ReadableStreamWrapper(raw_binary_read_channel)
        read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
        write_channel = self.__connection.makefile("wb", buffering=0)
        return read_channel, write_channel

    @staticmethod
    def _send_name(player: APIPlayer, read_channel: Iterator[Any],
                   write_channel: IO[bytes]) -> DispatchingReceiver:
        """
        Registers for the game being managed by the server connected to this client, then creates a
        DispatchingReceiver for it.
        :return: A DispatchingReceiver connected to the game
        """
        write_channel.write(json.dumps(player.name()).encode("utf-8"))
        dispatcher = DispatchingReceiver(player, read_channel, write_channel)
        return dispatcher
