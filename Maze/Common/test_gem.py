import pytest
import gem


# ------ Tests for Gem Constructor -------
# Tests to validate Gem constructor recognizes valid gem names and does not throw an exception
def test_generate_valid_gem_alexandrite():
    gem.Gem('alexandrite')


def test_generate_valid_gem_beryl():
    gem.Gem('beryl')


def test_generate_valid_gem_spinel():
    gem.Gem('spinel')


def test_generate_valid_gem_unakite():
    gem.Gem('unakite')


def test_generate_valid_gem_yellow_baguette():
    gem.Gem('yellow-baguette')


def test_generate_valid_gem_red_spinel_square_emerald_cut():
    gem.Gem('red-spinel-square-emerald-cut')


# Tests to validate Gem constructor recognizes invalid gem names and does throw an exception
def test_generate_invalid_gem1():
    with pytest.raises(ValueError) as error_message:
        gem.Gem('alexandria')
        assert error_message == 'Invalid Gem Name'


def test_generate_invalid_gem2():
    with pytest.raises(ValueError) as error_message:
        gem.Gem('not-a-gem')
        assert error_message == 'Invalid Gem Name'


def test_generate_invalid_gem3():
    with pytest.raises(ValueError) as error_message:
        gem.Gem('alexandritePear-shape')
        assert error_message == 'Invalid Gem Name'