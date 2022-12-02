from dataclasses import dataclass
from typing import Union, List

from Maze.Players.safe_api_player import SafeAPIPlayer


@dataclass
class WaitingPeriodPhase:
    """
    Represents the stage in which the server is still accepting signups.
    """
    period_num: int


@dataclass
class RunGamePhase:
    """
    Represents the stage in which the server is finished accepting signups and will run a game.
    """


@dataclass
class CancelledPhase:
    """
    Represents the stage in which the server is finished accepting signups and will not run a game.
    """


@dataclass
class SignupState:
    """
    Stores the server's current phase and list of signed-up players, in registration order (oldest-to-youngest).
    """
    phase: Union[WaitingPeriodPhase, RunGamePhase, CancelledPhase]
    players: List[SafeAPIPlayer]


@dataclass
class TimingEvent:
    """
    Tells a SignupState reducer to update according to an amount of elapsed seconds since waiting period 0 began.
    """
    elapsed: float


@dataclass
class CompletedHandshakeEvent:
    """
    Tells a SignupState reducer to update according to a completed handshake.
    """
    player: SafeAPIPlayer
