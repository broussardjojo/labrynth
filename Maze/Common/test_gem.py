import pytest
from .gem import Gem


# ------ Tests for Gem Constructor -------
# Tests to validate Gem constructor recognizes valid gem names and does not throw an exception
def test_generate_valid_gem_alexandrite():
    Gem('alexandrite')


def test_generate_valid_gem_beryl():
    Gem('beryl')


def test_generate_valid_gem_spinel():
    Gem('spinel')


def test_generate_valid_gem_unakite():
    Gem('unakite')


def test_generate_valid_gem_yellow_baguette():
    Gem('yellow-baguette')


def test_generate_valid_gem_red_spinel_square_emerald_cut():
    Gem('red-spinel-square-emerald-cut')


# Tests to validate Gem constructor recognizes invalid gem names and does throw an exception
def test_generate_invalid_gem1():
    with pytest.raises(ValueError) as error_message:
        Gem('alexandria')
    assert str(error_message.value) == 'Invalid Gem Name'


def test_generate_invalid_gem2():
    with pytest.raises(ValueError) as error_message:
        Gem('not-a-gem')
    assert str(error_message.value) == 'Invalid Gem Name'


def test_generate_invalid_gem3():
    with pytest.raises(ValueError) as error_message:
        Gem('alexandritePear-shape')
    assert str(error_message.value) == 'Invalid Gem Name'