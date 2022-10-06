from pathlib import Path


class Gem:
    """
    A Gem is a gem to collect in the game and has a name and image filepath.
    """
    def __init__(self, gem_name: str):
        """
        A constructor for a Gem, taking in a gem name and validating it before assigning it to the gem_name field
        :param gem_name: a string representing the name of the gem
        """
        gem_filepath = Path(f'../Resources/gems/{gem_name}.png')
        if gem_filepath.is_file():
            self.__gem_name = gem_name
            self.__gem_filepath = gem_filepath
        else:
            raise ValueError('Invalid Gem Name')

    def __eq__(self, other):
        if isinstance(other, Gem):
            return self.__gem_name == other.__gem_name
