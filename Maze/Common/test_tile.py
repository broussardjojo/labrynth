import pytest
from tile import Tile
from shapes import Corner, Line, TShaped, Cross
from gem import Gem
from direction import Direction


# ------ Examples of Shapes -------
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


# ------ Sample Tiles ------------------
@pytest.fixture
def cross_tile(basic_cross, amethyst_gem, emerald_gem):
    return Tile(basic_cross, amethyst_gem, emerald_gem)


@pytest.fixture
def corner_tile(basic_corner, amethyst_gem):
    return Tile(basic_corner, amethyst_gem, amethyst_gem)


@pytest.fixture
def line_tile(basic_line, emerald_gem, alexandrite_gem):
    return Tile(basic_line, emerald_gem, alexandrite_gem)


@pytest.fixture
def t_shape_tile(basic_t_shape, amethyst_gem):
    return Tile(basic_t_shape, amethyst_gem, amethyst_gem)


# ------- Tests for the Tile constructor --------------------------------
# Tests to validate Tile constructor accepts valid shapes and gems without throwing exceptions
def test_tile_constructor_corner(basic_corner, alexandrite_gem, amethyst_gem):
    Tile(basic_corner, alexandrite_gem, amethyst_gem)


def test_tile_constructor_line(basic_line, alexandrite_gem, emerald_gem):
    Tile(basic_line, alexandrite_gem, emerald_gem)


def test_tile_constructor_cross(basic_cross, emerald_gem):
    Tile(basic_cross, emerald_gem, emerald_gem)


def test_tile_constructor_t_shaped(basic_t_shape, amethyst_gem, emerald_gem):
    Tile(basic_t_shape, amethyst_gem, emerald_gem)


# ------- Tests for getting gems --------------------------------
# Tests to validate get_gems returns the gems on a Tile

def test_get_gems_cross(cross_tile, amethyst_gem, emerald_gem):
    assert cross_tile.get_gems() == [amethyst_gem, emerald_gem]


def test_get_gems_corner(corner_tile, amethyst_gem):
    assert corner_tile.get_gems() == [amethyst_gem, amethyst_gem]


def test_get_gems_line(line_tile, emerald_gem, alexandrite_gem):
    assert line_tile.get_gems() == [emerald_gem, alexandrite_gem]


# Tests same_gems_on_tiles
def test_same_gems_on_tiles1(corner_tile, amethyst_gem):
    assert corner_tile.same_gems_on_tiles(amethyst_gem, amethyst_gem)


def test_same_gems_on_tiles2(line_tile, emerald_gem, alexandrite_gem):
    assert line_tile.same_gems_on_tiles(emerald_gem, alexandrite_gem)


def test_same_gems_on_tiles3(cross_tile, amethyst_gem):
    assert not cross_tile.same_gems_on_tiles(amethyst_gem, amethyst_gem)


def test_same_gems_on_tiles4(corner_tile, amethyst_gem, emerald_gem):
    assert not corner_tile.same_gems_on_tiles(amethyst_gem, emerald_gem)


# Test the has_path method
def test_has_path_corner_tile_right(corner_tile):
    assert corner_tile.has_path(Direction.Right)


def test_has_path_corner_tile_not_bottom(corner_tile):
    assert not corner_tile.has_path(Direction.Down)


def test_has_path_cross_tile_left(cross_tile):
    assert cross_tile.has_path(Direction.Left)


def test_has_path_cross_tile_up(cross_tile):
    assert cross_tile.has_path(Direction.Up)


def test_has_path_line_tile_up(line_tile):
    assert line_tile.has_path(Direction.Up)


def test_has_path_line_tile_not_right(line_tile):
    assert not line_tile.has_path(Direction.Right)


def test_has_path_t_shape_tile_not_up(t_shape_tile):
    assert not t_shape_tile.has_path(Direction.Up)


def test_has_path_t_shape_tile_left(t_shape_tile):
    assert t_shape_tile.has_path(Direction.Left)
