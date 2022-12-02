import logging
import socket
from concurrent.futures import Executor
from typing import IO

from Maze.Players.api_player import APIPlayer
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Remote.player import RemotePlayer

log = logging.getLogger(__name__)


class SafeRemotePlayer(SafeAPIPlayer):
    """
    A class that represents a client of the referee, but always returns a `Future` instead of the direct
    result. This is designed to be used in combination with `gather_protected` and `await_protected`
    """

    player: APIPlayer
    __executor: Executor
    __connection: socket.socket
    __read_channel: IO[bytes]

    def __init__(self, player: APIPlayer, executor: Executor, connection: socket.socket,
                 binary_read_channel: IO[bytes]):
        """
        Creates a SafeAPIPlayer which wraps a given APIPlayer by executing its methods in an executor, and
        closes the given connection and read channel if/when the player is ejected.
        :param player: The APIPlayer to wrap
        :param executor: The ThreadPoolExecutor where the methods will be executed
        :param connection: The socket associated with the RemotePlayer
        :param binary_read_channel: A file-like readable stream tied to the socket
        """
        super().__init__(player, executor)
        self.__connection = connection
        self.__read_channel = binary_read_channel

    def on_kicked(self) -> None:
        """
        A method to tear down any resources used in the construction of this SafeAPIPlayer. This must not trigger
        any interaction with the wrapped APIPlayer, no matter if it is local or remote.
        :return: None
        """
        log.info("Closing %s", self.__connection.getpeername())
        try:
            self.__connection.shutdown(socket.SHUT_RDWR)
            self.__connection.close()
            log.info("Closing success")
        except OSError:
            log.error("Closing failed", exc_info=True)
        self.__read_channel.close()
