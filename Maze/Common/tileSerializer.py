from .utils import get_connector_from_shape
from ..Common.tile import Tile


def get_serialized_tile(tile: Tile) -> dict:
    gem_1, gem_2 = tile.get_gems()
    tile_dict = {
        "tilekey": get_connector_from_shape(tile.get_shape()),
        "1-image": str(gem_1),
        "2-image": str(gem_2)
    }
    return tile_dict


