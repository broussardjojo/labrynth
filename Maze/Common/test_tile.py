import pytest
from tile import Tile
from shapes import Corner, Line, TShaped, Cross
from gem import Gem


@pytest.fixture
def basic_corner():
    return Corner(0)


@pytest.fixture
def basic_line():
    return Line(0)


@pytest.fixture
def basic_t_shape():
    return TShaped(0)


@pytest.fixture
def basic_cross():
    return Cross()


@pytest.fixture
def alexandrite_gem():
    return Gem('alexandrite')


@pytest.fixture
def amethyst_gem():
    return Gem('amethyst')


@pytest.fixture
def emerald_gem():
    return Gem('emerald')


def test_tile_constructor_corner(basic_corner, alexandrite_gem, amethyst_gem):
    Tile(basic_corner, alexandrite_gem, amethyst_gem)


def test_tile_constructor_line(basic_line, alexandrite_gem, emerald_gem):
    Tile(basic_line, alexandrite_gem, emerald_gem)


def test_tile_constructor_cross(basic_cross, emerald_gem):
    Tile(basic_cross, emerald_gem, emerald_gem)


def test_tile_constructor_t_shaped(basic_t_shape, amethyst_gem, emerald_gem):
    Tile(basic_t_shape, amethyst_gem, emerald_gem)