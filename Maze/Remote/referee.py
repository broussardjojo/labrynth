import socket
from typing import IO, Iterator, Any

import ijson

from .remote_player_methods import RemotePlayerMethods
from ..Players.api_player import APIPlayer


class DispatchingReceiver:
    """
    A DispatchingReceiver handles a TCP connection which is expected to receive remote method call
    instructions, dispatches them as Python method calls, and sends the results in response
    """

    __player: APIPlayer
    __read_channel: Iterator[Any]
    __write_channel: IO[bytes]

    def __init__(self, player: APIPlayer, read_channel: Iterator[Any], write_channel: IO[bytes]):
        """
        Method to construct a DispatchingReceiver with a player, read channel, and write channel
        :param player: the APIPlayer that this receiver will ask to make logical game decisions
        :param read_channel: a generator of JSON values representing where responses will arrive
        :param write_channel: a BufferedIOBase representing where requests will go
        """
        self.__player = player
        self.__read_channel = read_channel
        self.__write_channel = write_channel

    @classmethod
    def from_socket(cls, player: APIPlayer, connection: socket.socket) -> "DispatchingReceiver":
        """
        Method to construct a DispatchingReceiver given a socket and APIPlayer
        :param player: the APIPlayer
        :param connection: a socket.socket connected to a program compatible with the Remote Interactions spec
        :return: A DispatchingReceiver
        """
        binary_read_channel = connection.makefile("rb", buffering=0)
        read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
        return cls(player, read_channel, connection.makefile("wb", buffering=0))

    def listen_forever(self) -> None:
        """
        Begins listening for remote method calls
        :return: None
        """
        for method_instruction in self.__read_channel:
            assert isinstance(method_instruction, list)
            assert len(method_instruction) == 2
            method_name, json_args = method_instruction
            RemotePlayerMethods.respond(self.__player, method_name, json_args, self.__write_channel)
