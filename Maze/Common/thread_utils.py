import sys
from concurrent import futures
from concurrent.futures import Future
from typing import List, TypeVar
from .utils import Nothing, Maybe, Just

DEFAULT_TIMEOUT = 10
T = TypeVar("T")


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
                    print(exc, file=sys.stderr)
    except futures.TimeoutError as exc:
        # The timeout of the `as_completed()` call was hit; we've received every result we can
        if debug:
            print(exc, file=sys.stderr)
    return results


def await_protected(future: "Future[T]", timeout_seconds=DEFAULT_TIMEOUT) -> Maybe[T]:
    """
    Attempts to return the result of the given future. If the task contained by the future raises an exception,
    or takes longer than the given timeout length in seconds, a Nothing() is returned.
    :param future: an instance of concurrent.futures.Future, which is running on a ThreadPoolExecutor
    :param timeout_seconds: a number of seconds
    :return: a Maybe, where Just(value) represents a success, and Nothing() represents a failure
    """
    return gather_protected([future], timeout_seconds=timeout_seconds)[0]
