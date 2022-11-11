from .utils import get_connector_from_shape
from ..Common.tile import Tile
from ..JSON.definitions import JSONTile


def get_serialized_tile(tile: Tile) -> JSONTile:
    gem_1, gem_2 = tile.get_gems()
    return {
        "tilekey": get_connector_from_shape(tile.get_shape()),
        "1-image": str(gem_1),
        "2-image": str(gem_2)
    }
