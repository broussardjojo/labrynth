from concurrent.futures import Executor
from typing import IO

from Maze.Players.api_player import APIPlayer
from Maze.Players.safe_api_player import SafeAPIPlayer
from Maze.Remote.player import RemotePlayer


class SafeRemotePlayer(SafeAPIPlayer):
    """
    A class that represents a client of the referee, but always returns a `Future` instead of the direct
    result. This is designed to be used in combination with `gather_protected` and `await_protected`
    """

    player: APIPlayer
    __executor: Executor
    __read_channel: IO[bytes]

    def __init__(self, player: RemotePlayer, executor: Executor, binary_read_channel: IO[bytes]):
        """
        Creates a SafeAPIPlayer which wraps a given APIPlayer by executing its methods in an executor, and
        closes the given read channel if/when the player is ejected.
        :param player: The APIPlayer to wrap
        :param executor: The ThreadPoolExecutor where the methods will be executed
        :param binary_read_channel: A file-like readable stream
        """
        super().__init__(player, executor)
        self.__read_channel = binary_read_channel

    def on_kicked(self) -> None:
        """
        A method to tear down any resources used in the construction of this SafeAPIPlayer. This must not trigger
        any interaction with the wrapped APIPlayer, no matter if it is local or remote.
        :return: None
        """
        self.__read_channel.close()
