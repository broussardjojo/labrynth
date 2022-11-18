import os
import re
from abc import ABC, abstractmethod
from json import JSONDecoder
from pathlib import Path
from typing import Generic, List, Tuple, Union, Any, Callable, TypeVar
from typing_extensions import Literal, NoReturn

from .position import Position
from .shapes import TShaped, Line, Corner, Cross, Shape
from ..JSON.definitions import JSONConnector

# Represents any type
T = TypeVar("T")

# Represents a result type
R = TypeVar("R")


def identity(x: T) -> T:
    """
    Takes one argument and returns it
    :param x: The argument
    :return: The argument
    """
    return x


def boxed(func: Callable[[T], R]) -> Callable[[Tuple[T]], Tuple[R]]:
    """
    Wraps the given function so that boxed(func)(x) == (func(x[0]),) - where x is a tuple with 1 element
    :param func: A function taking one argument
    :return: A wrapped function
    """
    return lambda box: (func(box[0]),)


class Maybe(ABC, Generic[T]):
    """
    Represents a value that may or may not be present; these cases are implemented by Just and Nothing, respectively.
    """
    is_present: bool

    @abstractmethod
    def get(self, message: str = "Missing Value") -> T:
        """
        Gets the value of the Maybe, or throws a ValueError with the given message if no value is present.
        :param message: A string to use as the error message
        :raises: ValueError when this is called on a Nothing
        """


class Nothing(Maybe[T]):
    """
    Represents the case where a Maybe[T] is absent.
    """
    is_present: Literal[False]

    def __init__(self):
        self.is_present = False

    def get(self, message: str = "Missing Value") -> NoReturn:
        """
        Gets the value of the Maybe, or throws a ValueError with the given message if no value is present.
        :param message: A string to use as the error message
        :raises: ValueError when this is called on a Nothing
        """
        raise ValueError(message)

    def __eq__(self, other: Any) -> bool:
        """
        Overrides the equals method for a Nothing
        :param other: The other object to compare against
        :return: True if other is a Nothing, otherwise False
        """
        return isinstance(other, Nothing)

    def __repr__(self) -> str:
        """
        Override for the repr method on a Nothing
        :return: A string representing this Nothing
        """
        return "Nothing()"


class Just(Maybe[T]):
    """
    Represents the case where a Maybe[T] is present.
    """
    is_present: Literal[True]
    value: T

    def __init__(self, value: T):
        self.is_present = True
        self.value = value

    def get(self, message: str = "Missing Value") -> T:
        """
        Gets the value of the Maybe, or throws a ValueError with the given message if no value is present.
        :param message: A string to use as the error message
        """
        return self.value

    def __eq__(self, other: Any) -> bool:
        """
        Overrides the equals method for a Just
        :param other: The other object to compare against
        :return: True if other is a Just with the same value, otherwise False
        """
        if isinstance(other, Just):
            return self.value == other.value
        return False

    def __repr__(self) -> str:
        """
        Override for the repr method on a Just
        :return: A string representing this Just
        """
        return f"Just({self.value})"


def remove_gem_extension(filename: Path) -> str:
    """
    Removes the file extension from a provided Path
    :param filename: a Path representing the filepath which should have it's extension removed
    :return: a string representing the name of the provided file without an extension
    """
    extensions = "".join(filename.suffix)
    stripped_filename = str(filename).replace(extensions, "")
    return stripped_filename


def generate_gem_list() -> List[str]:
    """
    Generates a list of all possible gem names, determined by the contents of the gems directory.
    :return: A list of strings representing all possible gem names
    """
    gem_list = []
    current_directory = Path(__file__).parent
    path_to_images = '../Resources/gems/'
    gem_directory = (current_directory / path_to_images).resolve()
    for filename in os.listdir(gem_directory):
        file = os.path.join(gem_directory, filename)
        if os.path.isfile(file):
            filepath = Path(filename)
            gem_list.append(remove_gem_extension(filepath))
    return gem_list


# Dictionary to convert a shape character to a Shape
shape_dict = {
    '└': Corner(0),
    '┌': Corner(1),
    '┐': Corner(2),
    '┘': Corner(3),
    '│': Line(0),
    '─': Line(1),
    '┬': TShaped(0),
    '┤': TShaped(1),
    '┴': TShaped(2),
    '├': TShaped(3),
    '┼': Cross()
}

inverse_shape_dict = {
    shape: connector
    for connector, shape in shape_dict.items()
}

ALL_NAMED_COLORS = ["purple", "orange", "pink", "red", "blue", "green", "yellow", "white", "black"]


def get_json_obj_list(input_data) -> List[Union[dict, str, int]]:
    """
    Read standard input one JSON object at a time and convert it into a list of dictionaries
    :return: A list of dictionaries representing the two inputs (a board and a starting coordinate)
    """
    decoder = JSONDecoder()
    json_obj_list = []
    while len(input_data) > 0:
        json_obj, index = decoder.raw_decode(input_data)
        json_obj_list.append(json_obj)
        input_data = input_data[index:]
        input_data = input_data.lstrip()
    return json_obj_list


def coord_custom_compare(coord_one: dict, coord_two: dict) -> int:
    """
    Custom comparator to compare two coordinates of this format: {"column#: col, "row#", row}
    :param coord_one: dictionary of this format: {"column#: col, "row#", row}
    :param coord_two: dictionary of this format: {"column#: col, "row#", row}
    :return: -1 if coord_one comes first in the grid, 1 if coord_two comes first in the grid, 0 if they are the same
    location (hopefully never for our use case)
    """
    if coord_one['row#'] < coord_two['row#']:
        return -1
    elif coord_one['row#'] > coord_two['row#']:
        return 1
    elif coord_one['column#'] < coord_two['column#']:
        return -1
    elif coord_one['column#'] > coord_two['column#']:
        return 1
    return 0


def get_euclidean_distance_between(position_one: Position, position_two: Position) -> int:
    """
    Determines the Euclidean distance between two Positions using the distance formula: (x1-x2)^2 + (y1-y2)^2
    NOTE: While the distance formula does take the square root of the result at the end, we chose not to do this
    as we are comparing which is larger and not by how much in the only use of this function, taking the square
    root would lead to either casting results to ints (inaccurate) or having to use floats (prone to error)
    :param position_one: The first Position (p1)
    :param position_two: The second Position (p2)
    :return: An int representing the euclidean distance between two given positions
    """
    return (position_one.get_row() - position_two.get_row()) ** 2 + \
           (position_one.get_col() - position_two.get_col()) ** 2


def get_connector_from_shape(shape: Shape) -> JSONConnector:
    """
    Gets the JSON connector (one of 11 unicode characters) that represents the given Shape
    :param shape: A Shape
    :return: A JSONConnector
    """
    return inverse_shape_dict[shape]


def is_valid_player_name(name: str) -> bool:
    """
    Method to determine if the provided name matches the spec:
    ^[a-zA-Z0-9]+$ and is between 1 and 20 characters
    :param name: a string representing the potential name to validate
    :return: True if the name is valid, otherwise False
    """
    name_regex = re.compile("^[a-zA-Z0-9]{1,20}$")
    return bool(re.search(name_regex, name))
