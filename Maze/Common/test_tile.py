import pytest

import tile


@pytest.fixture
def corner_one():
    return tile.Tile(False, True, True, False)


@pytest.fixture
def corner_two():
    return tile.Tile(True, False, True, False)


@pytest.fixture
def line_one():
    return tile.Tile(True, False, True, False)

@pytest.fixture
def line_two():
    return tile.Tile(True, False, True, False)


@pytest.fixture
def cross():
    return tile.Tile(True, False, True, False)


@pytest.fixture
def t_one():
    return tile.Tile(True, False, True, False)


@pytest.fixture
def t_two():
    return tile.Tile(True, False, True, False)


def test_rotate_90_degrees(tile1, tile2):
    tile1.rotate(1)
    assert tile1 == tile2
