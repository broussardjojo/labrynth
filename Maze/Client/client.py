import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator
from contextlib import contextmanager

import ijson

from Maze.Common.thread_utils import gather_protected
from Maze.Players.euclid import Euclid
from Maze.Remote.referee import DispatchingReceiver
from ..Players.api_player import APIPlayer, LocalPlayer

# The number of seconds that the client should wait before shutting down if it starts before the Server has.
WAIT_FOR_SERVER_DURATION = 15


class InvalidNameError(ValueError):
    """
    Represents an error caused by the player providing an invalid name in a server to player handshake
    """


class Client:
    """
    A class representing the server to run a game of Labyrinth
    """
    __host_name: str
    __port_num: int

    def __init__(self, host_name: str, port_num: int):
        """
        Constructor for a Client which will connect to a game server at the provided port number
        :param host_name: a string representing the host that the client will connect to
        :param port_num: an int representing the port that the client will connect to
        :raises ValueError: if a port number less than 1 or greater than 65535
        """
        self.__host_name = host_name
        if 0 < port_num < 65536:
            self.__port_num = port_num
        else:
            raise ValueError("Invalid port number supplied")

    @contextmanager
    def connect(self) -> Iterator[socket.socket]:
        """
        Yields a connection to the server. This method is responsible for retrying connection for up to
        WAIT_FOR_SERVER_DURATION seconds before raising an error.
        :raises: socket.timeout if the final attempt in the allotted time period fails.
        :return:
        """
        delay_end = time.time() + WAIT_FOR_SERVER_DURATION
        delay_remaining = WAIT_FOR_SERVER_DURATION
        while delay_remaining > 0:
            try:
                connection = socket.create_connection((self.__host_name, self.__port_num), timeout=min(delay_remaining, 4))
            except socket.timeout as error:
                delay_remaining = delay_end - time.time()
                if delay_remaining <= 0:
                    raise error
            else:
                yield connection
        raise RuntimeError("Timeout error failed to raise with no time remaining")

    def play_game(self, player: APIPlayer) -> None:
        """
        Connects to the game server, joins the game by sending the given player's name, and begins playing. For more
        details on the gameplay phase, see Maze.Remote.referee
        :return: A bool which is True if the player won, and False if they lost or were kicked out
        """
        with socket.create_connection((self.__host_name, self.__port_num)) as connection:
            binary_read_channel = connection.makefile("rb", buffering=0)
            read_channel = ijson.items(binary_read_channel, "", multiple_values=True)
            write_channel = connection.makefile("wb", buffering=0)
            write_channel.write(json.dumps(player.name()).encode("utf-8"))
            dispatcher = DispatchingReceiver(player, read_channel, write_channel)
            dispatcher.listen_forever()


def play_game_euclid(name: str) -> None:
    """
    Method to play a game of Labyrinth with the Euclid strategy over the network with a provided name
    :param name: A string representing the name of the LocalPlayer to use
    :return: None
    """
    client = Client("localhost", 9999)
    player = LocalPlayer(name, Euclid())
    client.play_game(player)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        gather_protected(
            [executor.submit(play_game_euclid, "dylan"), executor.submit(play_game_euclid, "thomas")],
            timeout_seconds=60, debug=True
        )
