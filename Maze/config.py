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

logging.basicConfig(level=_log_levels.get(os.getenv("LOG_LEVEL", ""), logging.WARNING),
                    format="%(asctime)s %(levelname)-8s %(threadName)-24s %(message)s")


@dataclass
class Config:
    """
    A configuration class to represent a number of game attributes that may change between testing and delivery
    environments.
    """
    referee_max_rounds: int
    """ The maximum number of rounds the Referee should run in a Labyrinth game. """

    referee_use_additional_goals: bool
    """ A flag to determine if the referee should assign additional goals after a player reaches their first goal."""

    referee_method_call_timeout: float
    """ The maximum amount of time, in seconds, the Referee should wait for a player to respond to a method call before
    ejecting them."""

    server_handshake_timeout: float
    """ The amount of time, in seconds, the Server should wait between a client connecting and a client sending their 
    name before dropping the connection."""

    server_waiting_period_seconds: float
    """ The amount of time, in seconds, the Server should spend accepting connections and sign-ups before checking
    whether a game can start with the current list of players. """

    server_number_of_waiting_periods: int
    """ The number of waiting periods the server should allow before it must either run or cancel a game. """

    server_minimum_players_to_start: int
    """ The amount of players that must be connected at the end of a server's connection period to launch a game."""

    server_maximum_players_to_start: int
    """ The maximum amount of players to start a game with. The server should immediately start a game if it reaches 
    this amount of players. """

    client_start_interval: float
    """ The amount of time in seconds xclients should wait between connecting successive clients. """

    client_retry_sleep_duration: float
    """ The amount of time in seconds a Client should wait after a failed connection attempt before retrying. """

    observer_update_interval: float
    """ The desired amount of time in between observer updates (recommended value: 1/60th of a second). """


CONFIG = Config(referee_max_rounds=1000,
                referee_use_additional_goals=False,
                referee_method_call_timeout=4,
                server_handshake_timeout=2,
                server_waiting_period_seconds=20,
                server_number_of_waiting_periods=2,
                server_minimum_players_to_start=2,
                server_maximum_players_to_start=6,
                client_start_interval=3,
                client_retry_sleep_duration=1,
                observer_update_interval=1.0 / 60,
                )
