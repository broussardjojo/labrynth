from typing import List
from .position import Position

from .player import Player


def make_list_of_players(player_dict_list: List[dict]) -> List[Player]:
    """
    Makes a list of Players given a list
    :param player_dict_list: A List of dictionaries of colors, current positions,
     and home positions in the following format:
    {"color": Named color or hex color string, "current": {"column#":0,"row#":0}, "home":{"column#":1,"row#":1}}
    :return: A List of Player objects representing the players defined in the provided json
    """
    player_list = []
    for player_dict in player_dict_list:
        current_position = Position(player_dict["current"]["row#"], player_dict["current"]["column#"], )
        home_position = Position(player_dict["home"]["row#"], player_dict["home"]["column#"],)
        player_color = player_dict["color"]
        player_list.append(Player.from_current_home_color(current_position, home_position, player_color))
    return player_list
