from .position import Position


def get_position_dict(position: Position) -> dict:
    """
    Method to get a dictionary representation of a Position
    :param position: a Position representing the position to translate
    :return: a dictionary of the format {'column#': int, 'row#': int}
    """
    return {'column#': position.get_col(), 'row#': position.get_row()}

def get_position_from_dict(pos_dict: dict) -> Position:
    """
    Method to get a dictionary representation of a Position
    :param position: a Position representing the position to translate
    :return: a dictionary of the format {'column#': int, 'row#': int}
    """
    return Position(pos_dict["row#"], pos_dict["column#"])
