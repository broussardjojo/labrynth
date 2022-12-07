import socket
from dataclasses import dataclass

from Maze.Remote.readable_stream_wrapper import ReadableStreamWrapper
from Maze.Remote.types import IOBytes


@dataclass
class Duplex:
    """
    Represents a connection which can send and receive bytes using two separate file-like objects (also refereed to as
    channels).
    """

    binary_read_channel: IOBytes
    write_channel: IOBytes

    @classmethod
    def from_socket(cls, connection: socket.socket) -> "Duplex":
        """
        Method to construct a Duplex given a socket
        :param connection: an open socket.socket
        :return: A Duplex
        """
        raw_binary_read_channel = connection.makefile("rb", buffering=0)
        binary_read_channel = ReadableStreamWrapper(raw_binary_read_channel)
        write_channel = connection.makefile("wb", buffering=0)
        return cls(binary_read_channel, write_channel)

    def close(self) -> None:
        """
        Closes both the channels associated with this duplex. Note that if this was created from a socket,
        SocketIO.close "doesn't close the underlying socket, except if all references to it have disappeared."
        :return: None
        """
        self.binary_read_channel.close()
        self.write_channel.close()
