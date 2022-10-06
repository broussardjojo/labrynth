import os
from pathlib import Path
from typing import List


def remove_gem_extension(filename: Path) -> str:
    extensions = "".join(filename.suffix)
    stripped_filename = str(filename).replace(extensions, "")
    return stripped_filename


def generate_gem_list() -> List[str]:
    gem_list = []
    gem_directory = "../Resources/gems"
    for filename in os.listdir(gem_directory):
        file = os.path.join(gem_directory, filename)
        if os.path.isfile(file):
            filepath = Path(filename)
            gem_list.append(remove_gem_extension(filepath))
    return gem_list


generate_gem_list()