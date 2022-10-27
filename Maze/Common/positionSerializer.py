from .position import Position


def get_position_string(position: Position):
    return {'column#': position.get_col(), 'row#': position.get_row()}
