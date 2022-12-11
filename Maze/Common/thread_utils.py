import logging
import time
from concurrent import futures
from concurrent.futures import Future
from typing import List, TypeVar, Union

from Maze.Common.utils import Nothing, Maybe, Just

DEFAULT_TIMEOUT = 10
T = TypeVar("T")
log = logging.getLogger(__name__)


def gather_protected(future_list: "List[Future[T]]", timeout_seconds: float = DEFAULT_TIMEOUT,
                     debug: bool = False) -> List[Maybe[T]]:
    """
    Aggregates the results of attempting each given future. For the future at index `i`, the returned list will contain:
        - a Just(value) at index `i` if the task returns a value within the given time limit
        - a Nothing() otherwise (this includes the case where the future's task raises an exception)
    :param future_list: a list of concurrent.futures.Future instances, each of which are running on a ThreadPoolExecutor
    :param timeout_seconds: a number of seconds
    :param debug: a bool representing whether or not to print errors caught
    :return: a Maybe, where Just(value) represents a success, and Nothing() represents a failure
    """
    results: List[Maybe[T]] = [Nothing() for _ in future_list]
    future_to_result_index = {future: idx for idx, future in enumerate(future_list)}
    try:
        for future in futures.as_completed(future_list, timeout=timeout_seconds):
            index = future_to_result_index.pop(future)
            # as_completed guarantees that `future` is completed, so `future.result()` won't block
            # however, if the future's task raised an exception, `future.result()` will raise the same one
            try:
                results[index] = Just(future.result())
            except Exception as exc:
                # The execution of the protected method raised an Exception
                if debug:
                    log.info("Future #{} of {}: Exception".format(index, len(future_list)), exc_info=exc)
    except futures.TimeoutError as exc:
        # The timeout of the `as_completed()` call was hit; we've received every result we can
        if debug:
            log.info("TimeoutError", exc_info=exc)
    return results


def await_protected(future: "Future[T]", timeout_seconds: float = DEFAULT_TIMEOUT) -> Maybe[T]:
    """
    Attempts to return the result of the given future. If the task contained by the future raises an exception,
    or takes longer than the given timeout length in seconds, a Nothing() is returned.
    :param future: an instance of concurrent.futures.Future, which is running on a ThreadPoolExecutor
    :param timeout_seconds: a number of seconds
    :return: a Maybe, where Just(value) represents a success, and Nothing() represents a failure
    """
    return gather_protected([future], timeout_seconds=timeout_seconds)[0]


def get_now_protected(future: "Future[T]") -> Union[BaseException, Maybe[T]]:
    """
    Attempts to retrieve the result of the given future without waiting.
    :param future: an instance of concurrent.futures.Future, which is running on a ThreadPoolExecutor
    :return: a Union[BaseException, Maybe[T]]. BaseException indicates that the future completed with that exception;
        Just(T) indicates that the future completed normally, and Nothing() indicates that the future is still running.
    """
    try:
        return Just(future.result(timeout=0))
    except futures.TimeoutError:
        return Nothing()
    except BaseException as exc:
        return exc


def sleep_interruptibly(delay_seconds: float, loop_interval: float = 0.1) -> None:
    """
    Sleeps for the given duration in seconds, using a loop so that the GIL does not block on a single `time.sleep`
    call.
    :param delay_seconds: The intended duration for sleep
    :param loop_interval: The maximum time to spend in one `time.sleep` call
    :return: None
    :raises: ValueError if loop_interval is negative
    """
    delay_end = time.time() + delay_seconds
    delay_remaining = delay_seconds
    while delay_remaining > 0:
        time.sleep(min(delay_remaining, loop_interval))
        delay_remaining = delay_end - time.time()
