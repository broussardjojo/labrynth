import pytest
from .shapes import TShaped, Cross, Corner, Line
from .direction import Direction


# ----- Examples -----
@pytest.fixture
def basic_corner():
    return Corner(0)


@pytest.fixture
def rotated_corner():
    return Corner(1)


@pytest.fixture
def double_rotated_corner():
    return Corner(2)


@pytest.fixture
def cross():
    return Cross()


@pytest.fixture
def cross2():
    return Cross()


@pytest.fixture
def basic_t_shape():
    return TShaped(0)


@pytest.fixture
def basic_line():
    return Line(0)


# ----- Testing Constructors -----
def test_valid_corner_constructor():
    Corner(0)


def test_valid_corner_constructor_rotated():
    Corner(100)


def test_invalid_corner_constructor():
    with pytest.raises(ValueError) as error_message:
        Corner(-1)
    assert str(error_message.value) == "Invalid Corner Shape"


def test_valid_line_constructor():
    Corner(0)


def test_valid_line_constructor_rotated():
    Corner(1)


def test_invalid_line_constructor():
    with pytest.raises(ValueError) as error_message:
        Line(-2)
    assert str(error_message.value) == "Invalid Line Shape"


def test_valid_t_shaped_constructor():
    TShaped(0)


def test_valid_t_shape_constructor_rotated():
    TShaped(31)


def test_invalid_t_shape_constructor():
    with pytest.raises(ValueError) as error_message:
        TShaped(-10)
    assert str(error_message.value) == "Invalid T-Shape"


# ----- Testing Rotate -----
def test_rotate_cross(cross, cross2):
    cross.rotate(1)
    assert cross == cross2


def test_rotate_corner(basic_corner, rotated_corner):
    basic_corner.rotate(1)
    assert basic_corner == rotated_corner


def test_rotate_corner_twice(basic_corner, double_rotated_corner):
    basic_corner.rotate(2)
    assert basic_corner == double_rotated_corner


# ----- Testing has_path -----
def test_has_path_corner_has_right(basic_corner):
    assert basic_corner.has_path(Direction.Right)


def test_has_path_corner_has_top(basic_corner):
    assert basic_corner.has_path(Direction.Up)


def test_has_path_corner_no_bottom(basic_corner):
    assert not basic_corner.has_path(Direction.Down)


def test_has_path_corner_no_left(basic_corner):
    assert not basic_corner.has_path(Direction.Left)


def test_has_path_cross(cross):
    assert cross.has_path(Direction.Left)


def test_has_path_line_up(basic_line):
    assert basic_line.has_path(Direction.Up)


def test_has_path_line_not_right(basic_line):
    assert not basic_line.has_path(Direction.Right)


def test_has_path_t_shape_right(basic_t_shape):
    assert basic_t_shape.has_path(Direction.Right)
