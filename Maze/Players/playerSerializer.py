from typing import List

from .euclid import Euclid
from .riemann import Riemann
from ..Common.position import Position
from .strategy import Strategy
from .player import Player
from ..Common.positionSerializer import get_position_dict, get_position_from_dict


def make_player_with_all_information(player_dict: dict, strategy: Strategy, goal: Position) -> Player:
    """
    Makes a player with its current position, home position, color, strategy, and goal
    NOTE: Makes arbitrary choice to name the player "Joe" and give an age of 10
    :param player_dict: a dictionary representing information about a player: current position, home position, and color
    :param strategy: a Strategy for this player to use
    :param goal: a Position representing the goal for the player to reach
    :return: a Player object created with the given information
    """
    current_position = Position(player_dict["current"]["row#"], player_dict["current"]["column#"], )
    home_position = Position(player_dict["home"]["row#"], player_dict["home"]["column#"], )
    player_color = player_dict["color"]
    return Player(home_position, goal, current_position, strategy, player_color, "Joe", 10)


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
        home_position = Position(player_dict["home"]["row#"], player_dict["home"]["column#"], )
        player_color = player_dict["color"]
        player_list.append(Player.from_current_home_color(current_position, home_position, player_color))
    return player_list


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
        "current": get_position_dict(player.get_current_position()),
        "home": get_position_dict(player.get_home_position()),
        "goto": get_position_dict(player.get_goal_position()),
        "color": player.get_color()
    }
    return player_dict


def make_list_of_players_given_info(list_of_names_and_strategies: List[List[str]],
                                    list_of_player_info: List[dict]) -> List[Player]:
    """
    Makes a 2-D list of players given a list of player names and strategies and a list of dictionaries containing player
    information
    :param list_of_names_and_strategies: a 2-D list that represents Player names and Strategies
    :param list_of_player_info: a list of dictionaries representing player information including their home position,
    goal position, current position, and color
    :return: a list of Players created by the given information
    """
    players = []
    for i in range(len(list_of_names_and_strategies)):
        home_position = get_position_from_dict(list_of_player_info[i]["home"])
        goal_position = get_position_from_dict(list_of_player_info[i]["goto"])
        current_position = get_position_from_dict(list_of_player_info[i]["current"])
        color = list_of_player_info[i]["color"]
        strategy = make_strategy(list_of_names_and_strategies[i][1])
        name = list_of_names_and_strategies[i][0]
        player = Player(home_position, goal_position, current_position, strategy, color, name, 10)
        players.append(player)
    return players


def make_strategy(strategy_name: str) -> Strategy:
    """
    Create either a Riemann or Euclid strategy
    :param strategy_name: either Riemann or Euclid
    :return: Either a Riemann or Euclid Strategy
    """
    if strategy_name == "Riemann":
        return Riemann()
    return Euclid()
