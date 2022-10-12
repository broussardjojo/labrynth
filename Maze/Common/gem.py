from pathlib import Path


class Gem:
    """
    A Gem is a gem to collect in the game and has a name and image filepath.
    """
    def __init__(self, gem_name: str):
        """
        A constructor for a Gem, taking in a gem name and validating it by checking it exists in our acceptable gems
        before assigning it to the gem_name field
        :param gem_name: a string representing the name of the gem
        """
        gem_filepath = self.__get_gem_filepath(gem_name)
        if gem_filepath.is_file():
            self.__gem_name = gem_name
            self.__gem_filepath = gem_filepath
        else:
            raise ValueError('Invalid Gem Name')

    def __eq__(self, other) -> bool:
        """
        Overrides equals for the Gem class. Two Gems are equal if their name is the same.
        :param other: Any, which represents the object being compared to this Gem
        :return: True if both objects are Gems and have the same gem_name, otherwise False
        """
        if isinstance(other, Gem):
            return self.__gem_name == other.__gem_name

    @staticmethod
    def __get_gem_filepath(gem_name: str) -> Path:
        """
        Get the filepath of a Gem based on the given string name
        :param gem_name: string representing the name of a Gem
        :return: a Path to a Gem's potential location
        """
        extension = ".png"
        current_directory = Path(__file__).parent
        path_to_images = f'../Resources/gems/{gem_name}'
        gem_filename = (current_directory / path_to_images).resolve()
        gem_filepath = Path(f'{gem_filename}{extension}')
        return gem_filepath

    def __str__(self):
        """
        Provides the name of this Gem as a string.
        :return: this Gem's name
        """
        return self.__gem_name
