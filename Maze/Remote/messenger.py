import json
from io import BufferedIOBase, TextIOWrapper, TextIOBase
from typing import overload, Literal, Optional, Tuple, Union

from typing_extensions import assert_never

from ..Common.board import Board
from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..JSON.serializers import position_to_json, redacted_state_to_json
from ..Players.api_player import Acknowledgement
from ..Players.move import Move, Pass

PlayerMethodName = Literal["setup", "propose_board0", "name", "take_turn", "win"]


class Messenger:
    """
    A Messenger handles a TCP connection which is intended to call remote methods on a player
    """

    __read_channel: TextIOBase
    __write_channel: TextIOBase

    def __init__(self, read_channel: BufferedIOBase, write_channel: BufferedIOBase):
        """
        Method to construct a Messenger with a read channel and write channel
        :param read_channel: a BufferedIOBase representing where responses will come from
        :param write_channel: a BufferedIOBase representing where requests will go
        """
        self.__read_channel = TextIOWrapper(read_channel, encoding="utf-8")
        self.__write_channel = TextIOWrapper(write_channel, encoding="utf-8")

    @overload
    def call(self, method_name: Literal["setup"], args: Tuple[Optional[RedactedState], Position]) -> Acknowledgement:
        pass

    @overload
    def call(self, method_name: Literal["propose_board0"], args: Tuple[int, int]) -> Board:
        pass

    @overload
    def call(self, method_name: Literal["name"], args: Tuple[()]) -> str:
        pass

    @overload
    def call(self, method_name: Literal["take_turn"], args: Tuple[RedactedState]) -> Union[Move, Pass]:
        pass

    @overload
    def call(self, method_name: Literal["win"], args: Tuple[bool]) -> Acknowledgement:
        pass

    def call(self, method_name, args):
        """
        A method to call a provided Player method with provided arguments
        :param method_name: A string representing the name of the method to call
        :param args: The arguments to call the given method with
        :return: The given method's return type
        """
        serialized_instruction = [self.__convert_method_name(method_name), *(self.__serialize_arg(arg) for arg in args)]
        json.dump(serialized_instruction, self.__write_channel)
        response = ""
        response += self.__read_channel.read(1024)
        # TODO: implement with non-blocking received
        return self.__deserialize_response(response)


    @staticmethod
    def __convert_method_name(method_name: PlayerMethodName) -> str:
        if method_name == "name":
            return "name"
        if method_name == "propose_board0":
            return "proposeBoard0"
        if method_name == "setup":
            return "setup"
        if method_name == "take_turn":
            return "takeTurn"
        if method_name == "win":
            return "win"
        assert_never(method_name)

    @staticmethod
    def __serialize_arg(arg: Union[RedactedState, Position, int, bool]):
        if isinstance(arg, Position):
            return position_to_json(arg)
        if isinstance(arg, RedactedState):
            return redacted_state_to_json(arg)
        return arg

    def __deserialize_response(self, response):
        pass
