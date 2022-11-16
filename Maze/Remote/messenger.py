import json
from typing import overload, Optional, Tuple, Union, IO, Iterator, Any, Dict, Callable
from typing_extensions import Literal

import ijson
from pydantic import parse_obj_as, StrictStr
from typing_extensions import assert_never

from ..Common.board import Board
from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..JSON.definitions import JSONChoice, JSONBoard, JSONPlayerMethodName
from ..JSON.deserializers import get_tile_grid_from_json, get_move_or_pass_from_json
from ..JSON.serializers import position_to_json, redacted_state_to_json
from ..Players.api_player import Acknowledgement
from ..Players.move import Move, Pass

PlayerMethodName = Literal["name", "propose_board0", "setup", "take_turn", "win"]


class Messenger:
    """
    A Messenger handles a TCP connection which is intended to call remote methods on a player
    """

    __read_channel: Iterator[Any]
    __write_channel: IO[bytes]

    def __init__(self, read_channel: IO[bytes], write_channel: IO[bytes]):
        """
        Method to construct a Messenger with a read channel and write channel
        :param read_channel: a BufferedIOBase representing where responses will come from
        :param write_channel: a BufferedIOBase representing where requests will go
        """
        self.__read_channel = ijson.items(read_channel, "", multiple_values=True)
        self.__write_channel = write_channel

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
        self.__write_channel.write(json.dumps(serialized_instruction).encode("utf-8"))
        # A number can be the top-level of a JSON stream, so to ensure that the receiver can
        # find the end of the record immediately, we send a trailing byte of whitespace.
        # This has no effect since we just wrote an array, but is kept here for consistency.
        self.__write_channel.write(b" ")
        # self.__read_channel is already mapping bytes to JSON values, we only need to create the correct model
        # for the JSON value in our application.
        return self.__deserialize_response(method_name, next(self.__read_channel))

    @staticmethod
    def __convert_method_name(method_name: PlayerMethodName) -> JSONPlayerMethodName:
        if method_name == "name":
            return "name"
        if method_name == "propose_board0":
            return "proposeBoard0"
        if method_name == "setup":
            return "setUp"
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

    @staticmethod
    def __deserialize_response(method_name: PlayerMethodName, response: Any):
        """
        Checks that the runtime type of the given response matches the expected JSON representation of the given
        method's return type, then returns our real representation of the given method's return value.
        :param method_name: One of "name", "propose_board0", "setup", "take_turn", or "win"
        :param response: An Any; should be the result of json.load or a compatible JSON deserializer
        :return: The type corresponding to the method name. See `Messenger.call`
        """
        transport_types: Dict[PlayerMethodName, Any] = {
            "name": StrictStr,
            "propose_board0": JSONBoard,
            "setup": Any,
            "take_turn": JSONChoice,
            "win": Any
        }
        transport_value = parse_obj_as(transport_types[method_name], response)
        serializer_map: Dict[PlayerMethodName, Callable[[Any], Any]] = {
            "propose_board0": lambda json_board: Board.from_list_of_tiles(get_tile_grid_from_json(json_board)),
            "take_turn": get_move_or_pass_from_json,
        }
        if method_name in serializer_map:
            serializer = serializer_map[method_name]
            return serializer(transport_value)
        return transport_value

    def __hash__(self) -> int:
        """
        Overrides the __hash__ method for Messengers. Uses the reference ID of the Messenger
        :return: An int representing the hash of the Messenger
        """
        return id(self)
