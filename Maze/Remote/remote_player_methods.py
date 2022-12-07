import json
from typing import Optional, Tuple, Union, IO, Iterator, Any, Callable, TypeVar, Generic

from pydantic import parse_obj_as
from typing_extensions import Literal, assert_never

from Maze.Common.position import Position
from Maze.Common.redacted_state import RedactedState
from Maze.Common.utils import boxed, identity
from Maze.JSON.definitions import JSONState, JSONCoordinate, JSONChoice, PlayerMethodName
from Maze.JSON.deserializers import (get_redacted_state_from_json,
                                     get_position_from_json, get_move_or_pass_from_json)
from Maze.JSON.serializers import move_to_json, pass_to_json, redacted_state_to_json, position_to_json
from Maze.Players.api_player import APIPlayer
from Maze.Players.move import Move, Pass
from Maze.Remote.types import IOBytes

TJsonArgs = TypeVar("TJsonArgs")
TArgs = TypeVar("TArgs")
TResult = TypeVar("TResult")
TJsonResult = TypeVar("TJsonResult")


class RemotePlayerMethod(Generic[TArgs, TJsonArgs, TResult, TJsonResult]):
    """
    A class that represents the steps required to either call a method or respond to a method call using
    the [MName, [Arguments, ...]] format described in https://course.ccs.neu.edu/cs4500f22/remote.html.

    The purpose of unifying the call and response code is a) to keep as much of our code using type hints as possible,
    and b) to have serialization methods near their corresponding deserialization methods.
    """
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

    def call(self, args: TArgs, read_channel: Iterator[Any], write_channel: IOBytes) -> TResult:
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

    def respond(self, player: APIPlayer, json_args: TJsonArgs, write_channel: IOBytes) -> None:
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
             write_channel: IOBytes) -> Literal["void"]:
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
             write_channel: IOBytes) -> Union[Move, Pass]:
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

    def call(self, args: Tuple[bool], read_channel: Iterator[Any], write_channel: IOBytes) -> Any:
        return super().call(args, read_channel, write_channel)


class RemotePlayerMethods:
    """
    Convenience class to hold the 3 implemented RemotePlayerMethods. Should not be constructed.
    """

    setup = _RemoteSetup()
    take_turn = _RemoteTakeTurn()
    win = _RemoteWin()

    @classmethod
    def respond(cls, player: APIPlayer, method_name: PlayerMethodName, json_args: Any,
                write_channel: IOBytes) -> None:
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
            cls.win.respond(player, json_args, write_channel)
        else:
            assert_never(method_name)
