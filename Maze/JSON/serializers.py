from typing import List, Tuple

from typing_extensions import assert_never

from .definitions import JSONDirection, JSONChoiceMove, JSONCoordinate, JSONRefereePlayer, JSONRefereeState, JSONBoard, \
    JSONConnector, JSONTreasure, JSONTile, OptionalJSONAction, JSONState, JSONPlayer, JSONChoicePass
from ..Common.board import Board
from ..Common.direction import Direction
from ..Common.player_details import PlayerDetails
from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..Common.referee_player_details import RefereePlayerDetails
from ..Common.state import State
from ..Common.tile import Tile
from ..Common.utils import get_connector_from_shape
from ..Players.move import Move, Pass


def direction_to_json(direction: Direction) -> JSONDirection:
    """
    Gets the string representation of the given direction
    :param direction: the Direction representing the direction to translate
    :return: a string representing a direction
    """
    if direction is Direction.DOWN:
        return "DOWN"
    elif direction is Direction.UP:
        return "UP"
    elif direction is Direction.RIGHT:
        return "RIGHT"
    elif direction is Direction.LEFT:
        return "LEFT"
    else:
        assert_never(direction)


def position_to_json(position: Position) -> JSONCoordinate:
    """
    Gets the JSON representation of the given position
    :param position: A Position
    :return: A JSONCoordinate dictionary in the format {"row#": int, "column#": int}
    """
    return {"row#": position.get_row(), "column#": position.get_col()}


def move_to_json(move: Move) -> JSONChoiceMove:
    """
    Gets the JSON representation of the given move
    :return: a List containing this Move's slide index, slide direction, spare tile rotation degrees,
     and avatar move JSONCoordinate
    """
    index = move.get_slide_index()
    direction = move.get_slide_direction()
    degrees_clockwise = move.get_spare_tile_rotation_degrees()
    destination_pos = move.get_destination_position()
    # Note that we convert to counterclockwise
    return (index,
            direction_to_json(direction),
            -degrees_clockwise % 360,
            position_to_json(destination_pos))


def pass_to_json(pass_instance: Pass) -> JSONChoicePass:
    """
    Gets the JSON representation of the given pass
    :return: the string "PASS"
    """
    return "PASS"


def __connectors_to_json(board: Board) -> List[List[JSONConnector]]:
    """
    Gets the JSON matrix version of the board's connectors
    :param board: A Board
    :return: A JSON matrix
    """
    tile_grid = board.get_tile_grid()
    return [
        [get_connector_from_shape(tile.get_shape()) for tile in row]
        for row in tile_grid
    ]


def __treasures_to_json(board: Board) -> List[List[JSONTreasure]]:
    """
    Gets the JSON matrix version of the board's connectors
    :param board: A Board
    :return: A JSON matrix
    """
    tile_grid = board.get_tile_grid()
    return [
        [[gem1.get_name(), gem2.get_name()] for gem1, gem2 in map(Tile.get_gems, row)]
        for row in tile_grid
    ]


def board_to_json(board: Board) -> JSONBoard:
    """
    Gets the JSON representation of the given board
    :param board: A Board
    :return: A dict in the format {"connectors":[...],"treasures":[...]}
    """
    return {
        "connectors": __connectors_to_json(board),
        "treasures": __treasures_to_json(board)
    }


def tile_to_spare_tile_json(tile: Tile) -> JSONTile:
    """
    Gets the spare tile JSON representation of the given tile
    :param tile: A Tile
    :return: A dict in the format {"tilekey":JSONConnector,"1-image":str,"2-image":str}
    """
    gem1, gem2 = tile.get_gems()
    return {
        "tilekey": get_connector_from_shape(tile.get_shape()),
        "1-image": gem1.get_name(),
        "2-image": gem2.get_name(),
    }


def referee_player_details_to_json(player: RefereePlayerDetails) -> JSONRefereePlayer:
    """
    Gets the JSON representation of the given referee player details
    :param player: A RefereePlayerDetails
    :return: A dict in the format {"current":{"row#":int,"column#":int},"home":{"row#":int,"column#":int},
    "goto":{"row#":int,"column#":int},"color":str}
    """
    return {
        "current": position_to_json(player.get_current_position()),
        "home": position_to_json(player.get_home_position()),
        "goto": position_to_json(player.get_goal_position()),
        "color": player.get_color()
    }


def player_details_to_json(player: PlayerDetails) -> JSONPlayer:
    """
    Gets the JSON representation of the given player details
    :param player: A PlayerDetails
    :return: A dict in the format {"current":{"row#":int,"column#":int},"home":{"row#":int,"column#":int},"color":str}
    """
    return {
        "current": position_to_json(player.get_current_position()),
        "home": position_to_json(player.get_home_position()),
        "color": player.get_color()
    }


def last_action_to_json(action_list: List[Tuple[int, Direction]]) -> OptionalJSONAction:
    """
    Gets the JSON representation of the last action in the given list, or None if empty
    :param action_list: A List[Tuple[int, Direction]], ordered from earliest to most recent move
    :return: Either a list [int, JSONDirection] or None
    """
    if len(action_list) == 0:
        return None
    index, direction = action_list[-1]
    return [index, direction_to_json(direction)]


def state_to_json(state: State) -> JSONRefereeState:
    """
    Gets the JSON representation of the given State, which must include player secrets
    :param state: A State
    :return: A dict in the format {"board":{"connectors":[...],"treasures":[...]},"spare":
    {"tilekey":JSONConnector,"1-image":str,"2-image":str},"plmt":[...],"last":[int, JSONDirection]|null}
    """
    return {'board': board_to_json(state.get_board()),
            'spare': tile_to_spare_tile_json(state.get_board().get_next_tile()),
            'plmt': [referee_player_details_to_json(player) for player in state.get_players()],
            'last': last_action_to_json(state.get_all_previous_non_passes())
            }


def redacted_state_to_json(state: RedactedState) -> JSONState:
    """
       Gets the JSON representation of the given RedactedState
       :param state: A RedactedState
       :return: A dict in the format {"board":{"connectors":[...],"treasures":[...]},"spare":
       {"tilekey":JSONConnector,"1-image":str,"2-image":str},"plmt":[...],"last":[int, JSONDirection]|null}
       """
    return {'board': board_to_json(state.get_board()),
            'spare': tile_to_spare_tile_json(state.get_board().get_next_tile()),
            'plmt': [player_details_to_json(player) for player in state.get_players()],
            'last': last_action_to_json(state.get_all_previous_non_passes())
            }
