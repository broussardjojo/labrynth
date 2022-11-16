import json
from typing import Optional, Tuple, Union, IO, Iterator, Any, Callable, TypeVar, Generic

import ijson
from pydantic import parse_obj_as
from typing_extensions import Literal
from typing_extensions import assert_never

from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..JSON.definitions import JSONState, JSONCoordinate, JSONChoice, PlayerMethodName
from ..JSON.deserializers import (get_redacted_state_from_json,
                                  get_position_from_json, get_move_or_pass_from_json)
from ..JSON.serializers import move_to_json, pass_to_json, redacted_state_to_json, position_to_json
from ..Players.api_player import APIPlayer
from ..Players.move import Move, Pass

T = TypeVar("T")
R = TypeVar("R")
TJsonArgs = TypeVar("TJsonArgs")
TArgs = TypeVar("TArgs")
TResult = TypeVar("TResult")
TJsonResult = TypeVar("TJsonResult")


class RemotePlayerMethod(Generic[TArgs, TJsonArgs, TResult, TJsonResult]):
    name: PlayerMethodName

    # __wrapped: Callable[[APIPlayer, TArgs], TResult]
    # __serialize_args: Callable[[TArgs], TJsonArgs]
    # __deserialize_args: Callable[[TJsonArgs], TArgs]
    # __serialize_result: Callable[[TResult], TJsonResult]
    # __deserialize_result: Callable[[TJsonResult], TResult]

    def __init__(
            self,
            name: PlayerMethodName,
            *,
            wraps: Callable[[APIPlayer, TArgs], TResult],
            serialize_args: Callable[[TArgs], TJsonArgs],
            deserialize_args: Callable[[TJsonArgs], TArgs],
            validate_args: Callable[[TJsonArgs], Any],
            serialize_result: Callable[[TResult], TJsonResult],
            deserialize_result: Callable[[TJsonResult], TResult],
            validate_result: Callable[[TJsonResult], Any]
    ):
        self.name = name
        self.__wrapped = wraps
        self.__serialize_args = serialize_args
        self.__deserialize_args = deserialize_args
        self.__validate_args = validate_args
        self.__serialize_result = serialize_result
        self.__deserialize_result = deserialize_result
        self.__validate_result = validate_result

    def call(self, args: TArgs, read_channel: Iterator[Any], write_channel: IO[bytes]) -> TResult:
        """
        Runs the pipelines:
            1. args | serialize_args | write
            2. read | validate_result | deserialize_result
        :param args: The arguments to the remote call
        :param read_channel: The JSON value channel on which to listen for a result
        :param write_channel: The byte channel on which to send a [MName, TJsonArgs] method call
        :return: The result of the remote call
        """
        json_args = self.__serialize_args(args)
        json_call = [self.name, json_args]
        write_channel.write(json.dumps(json_call).encode("utf-8"))
        json_result = next(read_channel)
        self.__validate_result(json_result)
        result = self.__deserialize_result(json_result)
        return result

    def respond(self, player: APIPlayer, json_args: TJsonArgs, write_channel: IO[bytes]) -> None:
        """
        Runs the pipelines:
            1. json_args | validate_args | deserialize_args
            2. (wrapped) | deserialize_result | write
        :param player: The APIPlayer which should logically respond to the method call
        :param json_args: The TJsonArgs which need to be deserialized and validated
        :param write_channel: The byte channel on which to send a TJsonResult response
        :return: None
        """
        self.__validate_args(json_args)
        args = self.__deserialize_args(json_args)
        result = self.__wrapped(player, args)
        json_result = self.__serialize_result(result)
        write_channel.write(json.dumps(json_result).encode("utf-8"))
        # A number can be the top-level of a JSON stream, so to ensure that the receiver can
        # find the end of the record immediately, we send a trailing byte of whitespace.
        write_channel.write(b" ")


def identity(x: T) -> T:
    """
    Takes one argument and returns it
    :param x: The argument
    :return: The argument
    """
    return x


def boxed(func: Callable[[T], R]) -> Callable[[Tuple[T]], Tuple[R]]:
    """
    Wraps the given function so that boxed(func)(x) == (func(x[0]),) - where x is a tuple with 1 element
    :param func: A function taking one argument
    :return: A wrapped function
    """
    return lambda box: (func(box[0]),)


class _RemoteSetup(
    RemotePlayerMethod[
        Tuple[Optional[RedactedState], Position],  # args
        Tuple[Union[Literal[False], JSONState], JSONCoordinate],  # json_args
        Any,  # result
        Literal["void"]  # json_result
    ]
):
    def __init__(self):
        super().__init__(
            "setup",
            wraps=lambda player, args: player.setup(args[0], args[1]),
            serialize_args=lambda pair: (
                redacted_state_to_json(pair[0]) if (pair[0] is not None) else False,
                position_to_json(pair[1])
            ),
            deserialize_args=lambda pair: (
                get_redacted_state_from_json(pair[0]) if (pair[0] is not False) else None,
                get_position_from_json(pair[1])
            ),
            validate_args=lambda args: parse_obj_as(
                Tuple[Union[Literal[False], JSONState], JSONCoordinate],
                args
            ),
            serialize_result=lambda _: "void",
            deserialize_result=lambda _: "void",
            validate_result=lambda _: (),
        )

    def call(self, args: Tuple[Optional[RedactedState], Position], read_channel: Iterator[Any],
             write_channel: IO[bytes]) -> Literal["void"]:
        return super().call(args, read_channel, write_channel)


class _RemoteTakeTurn(
    RemotePlayerMethod[
        Tuple[RedactedState],  # args
        Tuple[JSONState],  # json_args
        Union[Move, Pass],  # result
        JSONChoice  # json_result
    ]
):
    def __init__(self):
        super().__init__(
            "take-turn",
            wraps=lambda player, args: player.take_turn(args[0]),
            serialize_args=boxed(redacted_state_to_json),
            deserialize_args=boxed(get_redacted_state_from_json),
            validate_args=lambda args: parse_obj_as(
                Tuple[JSONState],
                args
            ),
            serialize_result=lambda res: move_to_json(res) if isinstance(res, Move) else pass_to_json(res),
            deserialize_result=get_move_or_pass_from_json,
            validate_result=lambda res: parse_obj_as(
                JSONChoice,
                res
            ),
        )

    def call(self, args: Tuple[RedactedState], read_channel: Iterator[Any],
             write_channel: IO[bytes]) -> Union[Move, Pass]:
        return super().call(args, read_channel, write_channel)


class _RemoteWin(
    RemotePlayerMethod[
        Tuple[bool],  # args
        Tuple[bool],  # json_args
        Any,  # result
        Literal["void"]  # json_result
    ]
):
    def __init__(self):
        super().__init__(
            "win",
            wraps=lambda player, args: player.win(args[0]),
            serialize_args=identity,
            deserialize_args=identity,
            validate_args=lambda args: parse_obj_as(Tuple[bool], args),
            serialize_result=lambda _: "void",
            deserialize_result=lambda _: "void",
            validate_result=lambda _: (),
        )

    def call(self, args: Tuple[bool], read_channel: Iterator[Any], write_channel: IO[bytes]) -> Any:
        return super().call(args, read_channel, write_channel)


class RemotePlayerMethods:
    setup = _RemoteSetup()
    take_turn = _RemoteTakeTurn()
    win = _RemoteWin()

    @classmethod
    def respond(cls, player: APIPlayer, method_name: PlayerMethodName, json_args: Any,
                write_channel: IO[bytes]) -> None:
        """
        Uses a given player to respond to a method call received from a remote server
        :param player: An APIPlayer representing the logical responder
        :param method_name: A PlayerMethodName representing the method to call
        :param json_args: The argument list received in the method call JSON
        :param write_channel: The byte channel on which to send a response
        :return: None
        """
        if method_name == "setup":
            cls.setup.respond(player, json_args, write_channel)
        elif method_name == "take-turn":
            cls.take_turn.respond(player, json_args, write_channel)
        elif method_name == "win":
            cls.take_turn.respond(player, json_args, write_channel)
        else:
            assert_never(method_name)


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
            assert len(method_instruction) == 2
            method_name, json_args = method_instruction
            RemotePlayerMethods.respond(self.__player, method_name, json_args, self.__write_channel)
