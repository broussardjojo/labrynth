import signal
from contextlib import contextmanager
from threading import RLock
from types import FrameType
from typing import Callable, Any, Set, Optional, ClassVar, Iterator

from Maze.Common.utils import Just


class SignalListener:
    """
    A class to dispatch SIGINT events, so that other components can handle user interrupts.
    """

    # Ignoring type error because this ClassVar is only None should only last from the declaration here
    # to the constructor call later in this file.
    instance: "ClassVar[SignalListener]" = None  # type: ignore
    __next_id: int
    __handlers: Set[Callable[[], Any]]
    __lock: RLock

    def __init__(self):
        """
        Creates a SignalListener and sets it up to dispatch to user-provided handlers. This should never be
        called outside signal_listener.py, use SignalListener.instance instead
        """
        if SignalListener.instance is not None:
            raise ValueError("Only one SignalListener should be constructed")
        self.__next_id = 0
        self.__handlers = set()
        self.__lock = RLock()
        signal.signal(signal.SIGINT, self.__handle)
        SignalListener.instance = self

    def __handle(self, _signum: int, _traceback: Optional[FrameType]) -> None:
        """
        Calls all currently registered handlers.
        :param _signum: Unused, provided by Python's signal event dispatcher
        :param _traceback: Unused, provided by Python's signal event dispatcher
        :return: None
        """
        with self.__lock:
            for handler in self.__handlers:
                handler()
        # https://docs.python.org/3/library/signal.html#signal.SIGINT
        # "Default action is to raise KeyboardInterrupt"
        raise KeyboardInterrupt()

    def add_handler(self, handler: Callable[[], Any]) -> None:
        """
        Register the given function to run when SIGINT is received.
        :param handler: A function taking zero arguments
        :return: None
        """
        with self.__lock:
            self.__handlers.add(handler)

    def remove_handler(self, handler: Callable[[], Any]) -> None:
        """
        Unregister the given function, so it no longer will run when SIGINT is received. This has no effect if
        the function isn't registered.
        :param handler: A function previously passed to add_handler()
        :return: None
        """
        with self.__lock:
            self.__handlers.discard(handler)


# Construct the singleton of SignalListener
SignalListener()


@contextmanager
def sigint_received_context() -> Iterator[Just[bool]]:
    """
    Creates a context value of Just(False), and registers a SIGINT handler to update the boxed bool to True.
    Exiting the context unregisters that handler.
    Intended usage:
        with sigint_received_context() as cancel_status:
            while not cancel_status.get():
                <blocking things>
    :return: Iterator[Just[bool]]
    """
    # beginning of context, no cancellation yet
    cancel_status = Just(False)

    def signal_responder() -> None:
        # user wants the program to stop
        cancel_status.value = True

    SignalListener.instance.add_handler(signal_responder)
    try:
        yield cancel_status
    finally:
        SignalListener.instance.remove_handler(signal_responder)
        if cancel_status.get():
            raise KeyboardInterrupt()