import concurrent.futures
import time
from concurrent.futures import ThreadPoolExecutor
from ..Referee.player_proxy import PlayerProxy
from ..Players.api_player import APIPlayer
from ..Players.riemann import Riemann
from .thread_utils import gather_protected
import pytest

from .utils import Just, Nothing


@pytest.fixture
def executor():
    tpe = ThreadPoolExecutor()
    try:
        yield tpe
    finally:
        tpe.shutdown(wait=False)


@pytest.fixture
def sample_api_player():
    return APIPlayer("Joe", Riemann())


# def test_empty_gather():
#     assert gather_protected([]) == []
#
#
# @pytest.mark.parametrize("sleep1, sleep2, sleep3", [(0, 1, 2), (1, 2, 0), (2, 1, 0), (2, 0, 1), (0, 2, 1), (1, 0, 2)])
# def test_gather_three_all_success(sleep1, sleep2, sleep3, executor):
#     future_list = [executor.submit(lambda res: time.sleep(seconds/10) or res, f"{idx + 1}")
#                    for idx, seconds in enumerate([sleep1, sleep2, sleep3])]
#     assert gather_protected(future_list) == [Just("1"), Just("2"), Just("3")]


# @pytest.mark.parametrize("sleep1, sleep2, sleep3", [(0, 6, 2)])
# def test_gather_three_one_timeout(sleep1, sleep2, sleep3, executor):
#     future_list = [executor.submit(lambda res: time.sleep(seconds) or res, f"{idx + 1}")
#                    for idx, seconds in enumerate([sleep1, sleep2, sleep3])]
#     assert gather_protected(future_list, timeout_seconds=5) == [Just("1"), Nothing(), Just("3")]


def test_win_success(sample_api_player):
    player_proxy = PlayerProxy(sample_api_player)
    assert player_proxy.won(True).is_present
    player_proxy.end()


def test_win_timeout(sample_api_player, monkeypatch):
    monkeypatch.setattr(sample_api_player, "won", lambda *args: time.sleep(100))
    player_proxy = PlayerProxy(sample_api_player, timeout=0.5)
    assert player_proxy.won(True) == Nothing()
    player_proxy.end()
