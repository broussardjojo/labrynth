from pathlib import Path

from Maze.Common.position import Position
from Maze.Common.utils import remove_gem_extension, generate_gem_list, get_euclidean_distance_between


# test the remove_gem_extension function
def test_remove_gem_extension_png1():
    assert remove_gem_extension(Path("hello.png")) == "hello"


def test_remove_gem_extension_png2():
    assert remove_gem_extension(Path("hey.png")) == "hey"


def test_remove_gem_extension_jpeg():
    assert remove_gem_extension(Path("scrumptious-apple-pie5.jpeg")) == "scrumptious-apple-pie5"


def test_remove_gem_extension_ppm():
    assert remove_gem_extension(Path("$-tree-34-.ppm")) == "$-tree-34-"


# test generate_gem_list
def test_generate_gem_list_length():
    gem_list = generate_gem_list()
    assert len(gem_list) == 102


def test_generate_gem_list_contains_amethyst():
    gem_list = generate_gem_list()
    assert "amethyst" in gem_list


def test_generate_gem_list_contains_yellow_baguette():
    gem_list = generate_gem_list()
    assert "yellow-baguette" in gem_list


def test_generate_gem_list_contains_green_princess_cut():
    gem_list = generate_gem_list()
    assert "green-princess-cut" in gem_list


# Test euclidean distance between positions
def test_get_euclidean_distance_between():
    position_one = Position(0, 3)
    position_two = Position(2, 3)
    assert get_euclidean_distance_between(position_one, position_two) == 4


def test_get_euclidean_distance_between_two():
    position_one = Position(-3, 9)
    position_two = Position(1, 2)
    assert get_euclidean_distance_between(position_one, position_two) == 65


def test_get_euclidean_distance_between_three():
    position_one = Position(12, 12)
    position_two = Position(12, 12)
    assert get_euclidean_distance_between(position_one, position_two) == 0
