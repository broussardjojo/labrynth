import json
from typing import Optional, Tuple, Union, IO, Iterator, Any, Dict, Callable

import ijson
from pydantic import parse_obj_as
from typing_extensions import Literal
from typing_extensions import assert_never

from ..Common.board import Board
from ..JSON.definitions import JSONPlayerMethodName, JSONState, JSONCoordinate
from ..JSON.deserializers import (get_redacted_state_from_json,
                                  get_position_from_json)
from ..JSON.serializers import move_to_json, pass_to_json, board_to_json
from ..Players.api_player import Acknowledgement, APIPlayer
from ..Players.move import Move, Pass

PlayerMethodName = Literal["name", "propose_board0", "setup", "take_turn", "win"]


# TTransport = TypeVar("TTransport")
# TArgs = TypeVar("TArgs")
# TReturn = TypeVar("TReturn")
#
# class ValidatingCaller(Generic[TTransport, TArgs, TReturn]):
#     def __init__(self, arg_getter: Callable[[TTransport], TArgs], method: Callable[[TArgs], TReturn]):
#         self.__arg_getter = arg_getter
#         self.__method = method
#
#     def call(self, transport_value: TTransport):
#         return self.__method(self.__arg_getter(transport_value))


class DispatchingReceiver:
    """
    A DispatchingReceiver handles a TCP connection which is expected to receive remote method call
    instructions, dispatches them as Python method calls, and sends the results in response
    """

    __player: APIPlayer
    __read_channel: Iterator[Any]
    __write_channel: IO[bytes]

    def __init__(self, player: APIPlayer, read_channel: IO[bytes], write_channel: IO[bytes]):
        """
        Method to construct a DispatchingReceiver with a player, read channel, and write channel
        :param player: the APIPlayer that this receiver will ask to make logical game decisions
        :param read_channel: a BufferedIOBase representing where responses will come from
        :param write_channel: a BufferedIOBase representing where requests will go
        """
        self.__player = player
        self.__read_channel = ijson.items(read_channel, "", multiple_values=True)
        self.__write_channel = write_channel

    def listen_forever(self) -> None:
        """
        Begins listening for remote method calls
        :return: None
        """
        for method_instruction in self.__read_channel:
            assert isinstance(method_instruction, list)
            assert len(method_instruction) >= 1
            json_method_name = parse_obj_as(JSONPlayerMethodName, method_instruction[0])
            method_name = self.__convert_method_name(json_method_name)
            method_args = self.__deserialize_args(method_name, method_instruction[1:])
            return_value = self.__call(method_name, method_args)
            json_return_value = self.__serialize_return_type(return_value)
            self.__write_channel.write(json.dumps(json_return_value).encode("utf-8"))
            # A number can be the top-level of a JSON stream, so to ensure that the receiver can
            # find the end of the record immediately, we send a trailing byte of whitespace.
            self.__write_channel.write(b" ")

    def __convert_method_name(self, method_name: JSONPlayerMethodName) -> PlayerMethodName:
        if method_name == "name":
            return "name"
        if method_name == "proposeBoard0":
            return "propose_board0"
        if method_name == "setUp":
            return "setup"
        if method_name == "takeTurn":
            return "take_turn"
        if method_name == "win":
            return "win"
        assert_never(method_name)

    @staticmethod
    def __serialize_return_type(arg: Union[Move, Pass, Board, str, Acknowledgement]):
        if isinstance(arg, Move):
            return move_to_json(arg)
        if isinstance(arg, Pass):
            return pass_to_json(arg)
        if isinstance(arg, Board):
            return board_to_json(arg)
        return arg

    def __call(self, method_name: PlayerMethodName, arguments: Any):
        if method_name == "name":
            return self.__player.name()
        if method_name == "propose_board0":
            return self.__player.propose_board0(*arguments)
        if method_name == "setup":
            return self.__player.setup(*arguments)
        if method_name == "take_turn":
            return self.__player.take_turn(*arguments)
        if method_name == "win":
            return self.__player.win(*arguments)
        assert_never(method_name)

    def __deserialize_args(self, method_name: PlayerMethodName, arguments: Any):
        """
        Checks that the runtime type of the given argument tuple matches the expected JSON representation of the given
        method's argument types, then returns our real representation of the given method's arguments.
        :param method_name: One of "name", "propose_board0", "setup", "take_turn", or "win"
        :param arguments: An Any; should be the result of json.load or a compatible JSON deserializer
        :return: The type corresponding to the method name. See `APIPlayer`
        """
        transport_types: Dict[PlayerMethodName, Any] = {
            "name": Tuple[()],
            "propose_board0": Tuple[int, int],
            "setup": Tuple[Optional[JSONState], JSONCoordinate],
            "take_turn": Tuple[JSONState],
            "win": Tuple[bool]
        }
        transport_value = parse_obj_as(transport_types[method_name], arguments)
        deserializer_map: Dict[PlayerMethodName, Callable[[Any], Any]] = {
            "setup": lambda pair: (
                get_redacted_state_from_json(pair[0]) if (pair[0] is not None) else None,
                get_position_from_json(pair[1])
            ),
            "take_turn": lambda box: (get_redacted_state_from_json(box[0]),)
        }
        if method_name in deserializer_map:
            deserializer = deserializer_map[method_name]
            return deserializer(transport_value)
        return transport_value
