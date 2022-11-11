from typing import List

from .player import Player
from ..JSON.serializers import position_to_json


def get_serialized_players(players: List[Player]) -> List[dict]:
    """
    Gets a list of dictionaries of player information from a list of players
    :param players: the list of players whose information is being turned into a dictionary
    :return: a list of dictionary representing the information of players from the given list
    """
    all_players = []
    for player in players:
        all_players.append(get_serialized_player(player))
    return all_players


def get_serialized_player(player: Player) -> dict:
    """
    Gets the information of a given player and turns it into a dictionary of player information
    :param player: the player whose information is being turned into a dictionary
    :return: a dictionary of information about the given player, including their current position, home position, goal
    position, and color
    """
    player_dict = {
        "current": position_to_json(player.get_current_position()),
        "home": position_to_json(player.get_home_position()),
        "goto": position_to_json(player.get_goal_position()),
        "color": player.get_color()
    }
    return player_dict
