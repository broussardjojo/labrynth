import logging
import os
from dataclasses import dataclass

_log_levels = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}

logging.basicConfig(level=_log_levels.get(os.getenv("LOG_LEVEL"), logging.WARNING))


@dataclass
class Config:
    """
    A configuration class to represent a number of game attributes that may change between testing and delivery
    environments.
    """
    referee_use_additional_goals: bool
    """ A flag to determine if the referee should assign additional goals after a player reaches their first goal."""

    referee_method_call_timeout: float
    """ The maximum amount of time, in seconds, the Referee should wait for a player to respond to a method call before
    ejecting them."""

    server_handshake_timeout: float
    """ The amount of time, in seconds, the Server should wait between a client connecting and a client sending their 
    name before dropping the connection."""

    server_minimum_players_to_start: int
    """ The amount of players that must be connected at the end of a server's connection period to launch a game."""

    server_maximum_players_to_start: int
    """ The maximum amount of players to start a game with. The server should immediately start a game if it reaches 
    this amount of players. """

    client_start_interval: float
    """ The amount of time in seconds xclients should wait between connecting successive clients. """


CONFIG = Config(referee_use_additional_goals=False,
                referee_method_call_timeout=4,
                server_handshake_timeout=2,
                server_minimum_players_to_start=2,
                server_maximum_players_to_start=6,
                client_start_interval=3
                )
