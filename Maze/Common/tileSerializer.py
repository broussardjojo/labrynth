from .shapes import Shape
from ..Common.tile import Tile
from ..Common.utils import shape_dict


def get_serialized_tile(tile: Tile) -> dict:
    gem_1, gem_2 = tile.get_gems()
    tile_dict = {
        "tilekey": get_connector_from_shape(tile.get_shape()),
        "1-image": str(gem_1),
        "2-image": str(gem_2)
    }
    return tile_dict


def get_connector_from_shape(shape: Shape) -> str:
    return list(shape_dict.keys())[list(shape_dict.values()).index(shape)]
