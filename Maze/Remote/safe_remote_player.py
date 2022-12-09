import logging
import socket
from concurrent.futures import Executor

import ijson

from Maze.Players.api_player import APIPlayer
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Remote.duplex import Duplex
from Maze.Remote.player import RemotePlayer

log = logging.getLogger(__name__)


class SafeRemotePlayer(SafeAPIPlayer):
    """
    A class that represents a client of the referee, but always returns a `Future` instead of the direct
    result. This is designed to be used in combination with `gather_protected` and `await_protected`
    """

    player: APIPlayer
    __executor: Executor
    __duplex: Duplex

    def __init__(self, player: APIPlayer, executor: Executor, duplex: Duplex):
        """
        Creates a SafeAPIPlayer which wraps a given APIPlayer by executing its methods in an executor, and
        closes the given connection and read channel if/when the player is ejected.
        :param player: The APIPlayer to wrap
        :param executor: The ThreadPoolExecutor where the methods will be executed
        :param duplex: The Duplex associated with the RemotePlayer
        """
        super().__init__(player, executor)
        self.__executor = executor
        self.__duplex = duplex

    @classmethod
    def from_socket(cls, name: str, executor: Executor, connection: socket.socket) -> "SafeRemotePlayer":
        """
        Method to construct a RemotePlayer given a socket
        :param name: the player's name
        :param executor: The ThreadPoolExecutor where the methods will be executed
        :param connection: a socket.socket connected to a program compatible with the Remote Interactions spec
        :return: A RemotePlayer
        """
        duplex = Duplex.from_socket(connection)
        read_channel = ijson.items(duplex.binary_read_channel, "", multiple_values=True)
        api_player = RemotePlayer(name, read_channel, duplex.write_channel)
        return cls(api_player, executor, duplex)

    def on_kicked(self) -> None:
        """
        A method to tear down any resources used in the construction of this SafeAPIPlayer. This must not trigger
        any interaction with the wrapped APIPlayer, no matter if it is local or remote.
        :return: None
        """
        try:
            self.__duplex.close()
        except OSError:
            log.error("Closing failed", exc_info=True)
