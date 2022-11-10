import sys
from queue import Queue, Full as QueueFullError, Empty as QueueEmptyError
from threading import Thread
from typing import Callable, Any, Optional

from ..Common.utils import Maybe, Just, Nothing
from ..Players.api_player import LocalPlayer

Acknowledgement = Any
DEFAULT_TIMEOUT = 10


class PlayerProxy:
    __work_queue: "Queue[Optional[Callable[[], Any]]]"
    __result_queue: "Queue[Any]"
    __player: LocalPlayer
    __thread: Thread
    __timeout_seconds: float

    def __init__(self, player: LocalPlayer, timeout: float = DEFAULT_TIMEOUT):
        self.__player = player
        self.__work_queue = Queue(maxsize=1)
        self.__result_queue = Queue(maxsize=1)
        self.__timeout_seconds = timeout
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self) -> None:
        while True:
            action = self.__work_queue.get()
            if action is None:
                break
            self.__result_queue.put(action())

    def end(self) -> None:
        self.__work_queue.put_nowait(None)

    def win(self, did_win: bool) -> Maybe[Acknowledgement]:
        try:
            self.__work_queue.put_nowait(lambda: self.__player.win(did_win))
            return Just(self.__result_queue.get(timeout=self.__timeout_seconds))
        except (QueueEmptyError, QueueFullError) as e:
            print(e, file=sys.stderr)
            return Nothing()

