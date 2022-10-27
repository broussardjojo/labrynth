from typing import List
from Maze.Common.position import Position
from .strategy import Strategy
from Maze.Players.player import Player


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
        home_position = Position(player_dict["home"]["row#"], player_dict["home"]["column#"],)
        player_color = player_dict["color"]
        player_list.append(Player.from_current_home_color(current_position, home_position, player_color))
    return player_list
