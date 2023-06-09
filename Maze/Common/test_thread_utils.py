import functools
from concurrent.futures import ThreadPoolExecutor
import pytest

from Maze.Players.api_player import LocalPlayer
from Maze.Players.riemann import Riemann
from Maze.Common.thread_utils import gather_protected, sleep_interruptibly
from Maze.Common.utils import Just, Nothing


@pytest.fixture
def executor():
    tpe = ThreadPoolExecutor()
    try:
        yield tpe
    finally:
        tpe.shutdown(wait=False)


@pytest.fixture
def sample_api_player():
    return LocalPlayer("Joe", Riemann())


def delayed_identity(delay_seconds, arg):
    sleep_interruptibly(delay_seconds)
    return arg


def throw_if(should_throw, return_supplier_or_val):
    if should_throw:
        raise ValueError()
    return return_supplier_or_val() if callable(return_supplier_or_val) else return_supplier_or_val


def test_empty_gather():
    assert gather_protected([]) == []


@pytest.mark.parametrize("sleep1, sleep2, sleep3", [
    (0, 50, 100),
    (50, 100, 0),
    (100, 50, 0),
    (100, 0, 50),
    (0, 100, 50),
    (50, 0, 100)
])
def test_gather_three_all_success(sleep1, sleep2, sleep3, executor):
    future_list = [executor.submit(delayed_identity, millis / 1000, f"{idx + 1}")
                   for idx, millis in enumerate([sleep1, sleep2, sleep3])]
    assert gather_protected(future_list) == [Just("1"), Just("2"), Just("3")]


@pytest.mark.parametrize("sleep1, sleep2, sleep3, expected", [
    (1000, 50, 50, [Nothing(), Just("2"), Just("3")]),
    (50, 1000, 50, [Just("1"), Nothing(), Just("3")]),
    (50, 50, 1000, [Just("1"), Just("2"), Nothing()]),
])
def test_gather_three_one_timeout(sleep1, sleep2, sleep3, expected, executor):
    future_list = [executor.submit(delayed_identity, millis / 1000, f"{idx + 1}")
                   for idx, millis in enumerate([sleep1, sleep2, sleep3])]
    assert gather_protected(future_list, timeout_seconds=0.5) == expected


@pytest.mark.parametrize("raise1, raise2, raise3, expected", [
    (True, False, False, [Nothing(), Just("2"), Just("3")]),
    (False, True, False, [Just("1"), Nothing(), Just("3")]),
    (False, False, True, [Just("1"), Just("2"), Nothing()]),
])
def test_gather_three_one_exception(raise1, raise2, raise3, expected, executor):
    future_list = [executor.submit(throw_if, should_throw, f"{idx + 1}")
                   for idx, should_throw in enumerate([raise1, raise2, raise3])]
    assert gather_protected(future_list, timeout_seconds=0.5) == expected


# Note: -1 means it should throw an exception
@pytest.mark.parametrize("sleep1, sleep2, sleep3, expected", [
    (-1, 1000, 50, [Nothing(), Nothing(), Just("3")]),
    (-1, 50, 1000, [Nothing(), Just("2"), Nothing()]),
    (1000, -1, 50, [Nothing(), Nothing(), Just("3")]),
    (50, -1, 1000, [Just("1"), Nothing(), Nothing()]),
    (1000, 50, -1, [Nothing(), Just("2"), Nothing()]),
    (50, 1000, -1, [Just("1"), Nothing(), Nothing()]),
])
def test_gather_three_one_timeout_one_exception(sleep1, sleep2, sleep3, expected, executor):
    future_list = [executor.submit(throw_if, millis < 0, functools.partial(delayed_identity, millis / 1000, f"{idx + 1}"))
                   for idx, millis in enumerate([sleep1, sleep2, sleep3])]
    assert gather_protected(future_list, timeout_seconds=0.5) == expected

# def test_win_success(sample_api_player):
#     player_proxy = PlayerProxy(sample_api_player)
#     assert player_proxy.win(True).is_present
#     player_proxy.end()
#
#
# def test_win_timeout(sample_api_player, monkeypatch):
#     monkeypatch.setattr(sample_api_player, "win", lambda *args: time.sleep(100))
#     player_proxy = PlayerProxy(sample_api_player, timeout=0.5)
#     assert player_proxy.win(True) == Nothing()
#     player_proxy.end()
