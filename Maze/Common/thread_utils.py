from concurrent import futures
from concurrent.futures import Future
from typing import List, TypeVar
from .utils import Nothing, Maybe, Just

DEFAULT_TIMEOUT = 10
T = TypeVar("T")


def gather_protected(future_list: "List[Future[T]]", timeout_seconds=DEFAULT_TIMEOUT) -> List[Maybe[T]]:
    results: List[Maybe[T]] = [Nothing() for _ in future_list]
    future_to_result_index = {future: idx for idx, future in enumerate(future_list)}
    try:
        for future in futures.as_completed(future_list, timeout=timeout_seconds):
            index = future_to_result_index.pop(future)
            try:
                results[index] = Just(future.result())
            except Exception:
                # The execution of the protected method raised an Exception
                pass
    except TimeoutError:
        for future in future_to_result_index.keys():
            future.cancel()
        # The timeout of the `as_completed()` call was hit; we've received every result we can
        pass
    return results
