from copy import deepcopy
from typing import List, Tuple, cast

from typing_extensions import assert_never

from Maze.Common.board import Board
from Maze.Common.direction import Direction
from Maze.Common.gem import Gem
from Maze.Common.position import Position
from Maze.Common.state import State
from Maze.Common.tile import Tile
from Maze.Common.utils import shape_dict
from Maze.JSON.definitions import JSONBoard, JSONTreasure, JSONState, JSONConnector, JSONDirection, JSONPlayer, \
    JSONAction, JSONPlayerSpecElement, JSONStrategyDesignation, JSONBadPlayerSpecElement, JSONBadMethod, \
    JSONBadPlayerSpec, JSONPlayerSpec, JSONRefereeState, JSONCoordinate, JSONRefereePlayer
from Maze.Players.api_player import LocalPlayer, APIPlayer, BadMethodName, BadLocalPlayer
from Maze.Players.euclid import Euclid
from Maze.Players.player import Player
from Maze.Players.riemann import Riemann
from Maze.Players.strategy import Strategy


def get_position_from_json(json_coordinate: JSONCoordinate) -> Position:
    """
    Creates the Position represented by the JSON
    :param json_coordinate: a JSONCoordinate
    :return: a Position
    """
    return Position(json_coordinate["row#"], json_coordinate["column#"])


def get_gems_from_json(gem_name_list: JSONTreasure) -> Tuple[Gem, Gem]:
    """
    Retrieve a pair of gems given a list of Gem names
    :param gem_name_list: List of Gem names (hopefully two for our use case)
    :return: Two Gems objects
    """
    return Gem(gem_name_list[0]), Gem(gem_name_list[1])


def get_tile_from_json(tilekey: JSONConnector, treasure: JSONTreasure) -> Tile:
    """
    Creates the Tile corresponding to the JSON pieces
    :param tilekey: The shape of the tile's connector
    :param treasure: The two gems on the tile
    :return: a Tile
    """
    shape = shape_dict[tilekey]
    gem1, gem2 = get_gems_from_json(treasure)
    return Tile(shape, gem1, gem2)


def get_tile_grid_from_json(board_dict: JSONBoard) -> List[List[Tile]]:
    """
    Makes a board given a dictionary of connectors and treasures
    :param board_dict: A dictionary of connectors and treasures in the following format
    {"connectors": List[List[Shape Characters]], "treasures": List[List[List[Gem Name Strings]]]
    :return: A Board object filled with all the tiles designated by the provided dictionary
    """
    tile_grid: List[List[Tile]] = []
    for row, json_tile_row in enumerate(board_dict['connectors']):
        tile_row: List[Tile] = []
        for col, json_tile in enumerate(json_tile_row):
            tile_row.append(get_tile_from_json(json_tile, board_dict["treasures"][row][col]))
        tile_grid.append(tile_row)
    return tile_grid


def get_player_details_from_json(json_player: JSONPlayer) -> Player:
    """
    Creates the Player represented by the JSON
    :param json_player: A dictionary with the format
    {"color": Named color or hex color string, "current": {"column#":0,"row#":0}, "home":{"column#":1,"row#":1}}
    :return: A List of Player objects representing the players defined in the provided json
    """
    current_position = get_position_from_json(json_player["current"])
    home_position = get_position_from_json(json_player["home"])
    player_color = json_player["color"]
    return Player.from_current_home_color(current_position, home_position, player_color)


def get_direction_from_json(direction_str: JSONDirection) -> Direction:
    """
    Method to translate a string to one of four Directions: Down, Up, Right, and Left
    :param direction_str: a string representing one of four directions
    :return: a Direction representing a translated direction
    """
    if direction_str == "DOWN":
        return Direction.Down
    if direction_str == "UP":
        return Direction.Up
    if direction_str == "RIGHT":
        return Direction.Right
    return Direction.Left


def get_previous_move_from_json(json_action: JSONAction) -> Tuple[int, Direction]:
    """
    A method to get the previous move from an int and string
    :param json_action: a List containing two elements ([int, JSONDirection])
    :return: a Tuple containing the given int and translated Direction
    """
    index = cast(int, json_action[0])
    json_direction = cast(JSONDirection, json_action[1])
    return index, get_direction_from_json(json_direction)


def get_state_from_json_state(json_state: JSONState) -> State:
    """
    Creates the State represented by the JSON, without player secrets
    TODO: Make this actually without player secrets, instead of with incorrect ones
    :param json_state: a dictionary containing values for "board", "spare", "plmt", and "last"
    :return: a State
    """
    tile_grid = get_tile_grid_from_json(json_state["board"])
    json_treasure = [json_state["spare"]["1-image"], json_state["spare"]["2-image"]]
    spare_tile = get_tile_from_json(json_state["spare"]["tilekey"], json_treasure)
    player_details = [get_player_details_from_json(json_player) for json_player in json_state["plmt"]]
    previous_moves: List[Tuple[int, Direction]] = []
    if json_state["last"] is not None:
        previous_moves.append(get_previous_move_from_json(json_state["last"]))
    board = Board(tile_grid, spare_tile)
    return State.from_current_state(board, player_details, previous_moves)


def get_referee_player_details_from_json(json_referee_player: JSONRefereePlayer) -> Player:
    """
    Creates the Player represented by the JSON
    :param json_referee_player: A dictionary with the format
    {"color": Named color or hex color string, "current": {"column#":0,"row#":0}, "home":{"column#":1,"row#":1},
     "goto":{"column#":1,"row#":1}}
    :return: A List of Player objects representing the players defined in the provided json
    """
    current_position = get_position_from_json(json_referee_player["current"])
    home_position = get_position_from_json(json_referee_player["home"])
    goal_position = get_position_from_json(json_referee_player["goto"])
    player_color = json_referee_player["color"]
    return Player(home_position, goal_position, current_position, player_color)


def get_state_from_json_referee_state(json_state: JSONRefereeState) -> State:
    """
    Creates the State represented by the JSON, with player secrets
    :param json_state: a dictionary containing values for "board", "spare", "plmt", and "last"
    :return: a State
    """
    tile_grid = get_tile_grid_from_json(json_state["board"])
    json_treasure = [json_state["spare"]["1-image"], json_state["spare"]["2-image"]]
    spare_tile = get_tile_from_json(json_state["spare"]["tilekey"], json_treasure)
    player_details = [get_referee_player_details_from_json(json_player) for json_player in json_state["plmt"]]
    previous_moves: List[Tuple[int, Direction]] = []
    if json_state["last"] is not None:
        previous_moves.append(get_previous_move_from_json(json_state["last"]))
    board = Board(tile_grid, spare_tile)
    return State.from_current_state(board, player_details, previous_moves)


def get_strategy_from_json(json_strategy_designation: JSONStrategyDesignation) -> Strategy:
    """
    Creates the strategy represented by the JSON
    :param json_strategy_designation: a string, either "Riemann" or "Euclid"
    :return: a Strategy
    """
    if json_strategy_designation == "Riemann":
        return Riemann()
    elif json_strategy_designation == "Euclid":
        return Euclid()
    else:
        assert_never(json_strategy_designation)


def get_api_player_from_json(json_player_spec_el: JSONPlayerSpecElement) -> APIPlayer:
    """
    Creates the good API player represented by the JSON
    :param json_player_spec_el: a list with two elements: [name, strategy_designation]
    :return: an APIPlayer
    """
    name = cast(str, json_player_spec_el[0])
    strategy_designation = cast(JSONStrategyDesignation, json_player_spec_el[1])
    return LocalPlayer(name, get_strategy_from_json(strategy_designation))


def get_bad_api_player_from_json(json_bad_player_spec_el: JSONBadPlayerSpecElement) -> APIPlayer:
    """
    Creates the bad API player represented by the JSON
    :param json_bad_player_spec_el: a list with two elements: [name, strategy_designation, bad_method_name]
    :return: an APIPlayer
    """
    name = cast(str, json_bad_player_spec_el[0])
    strategy_designation = cast(JSONStrategyDesignation, json_bad_player_spec_el[1])
    json_bad_method = cast(JSONBadMethod, json_bad_player_spec_el[2])
    strategy = get_strategy_from_json(strategy_designation)
    if json_bad_method == "setUp":
        return BadLocalPlayer(name, strategy, "setup")
    elif json_bad_method == "takeTurn":
        return BadLocalPlayer(name, strategy, "take_turn")
    elif json_bad_method == "win":
        return BadLocalPlayer(name, strategy, "win")
    else:
        assert_never(json_bad_method)


def get_api_player_list_from_bad_player_spec_json(json_bad_player_spec: JSONBadPlayerSpec) -> List[APIPlayer]:
    """
    Creates the list of API players (which can be good or bad) represented by JSON
    :param json_bad_player_spec: a list of Union[JSONBadPlayerSpecElement, JSONPlayerSpecElement]
    :return: a list of APIPlayers
    """
    result: List[APIPlayer] = []
    for json_ps in json_bad_player_spec:
        if len(json_ps) == 2:
            result.append(get_api_player_from_json(cast(JSONPlayerSpecElement, json_ps)))
        else:
            result.append(get_bad_api_player_from_json(cast(JSONBadPlayerSpecElement, json_ps)))
    return result


def get_api_player_list_from_player_spec_json(json_player_spec: JSONPlayerSpec) -> List[APIPlayer]:
    """
    Creates the list of all good API players represented by JSON
    :param json_player_spec: a list of JSONPlayerSpecElement
    :return: a list of APIPlayers
    """
    return get_api_player_list_from_bad_player_spec_json(json_player_spec)
