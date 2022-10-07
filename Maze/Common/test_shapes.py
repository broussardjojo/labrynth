import pytest
from shapes import TShaped, Cross, Corner, Line


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
