import os
from pathlib import Path
from typing import List
from .direction import Direction


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


def get_opposite_direction(input_direction: Direction) -> Direction:
    if input_direction == Direction.Up:
        return Direction.Down
    if input_direction == Direction.Down:
        return Direction.Up
    if input_direction == Direction.Right:
        return Direction.Left
    if input_direction == Direction.Left:
        return Direction.Right
