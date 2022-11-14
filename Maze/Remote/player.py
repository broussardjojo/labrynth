from typing import Union, Optional

from ..Common.board import Board
from ..Common.position import Position
from ..Common.redacted_state import RedactedState
from ..Players.api_player import APIPlayer, Acknowledgement
from ..Players.move import Move, Pass


class RemotePlayer(APIPlayer):
    def setup(self, state: Optional[RedactedState], goal_position: Position) -> Acknowledgement:
        pass

    def propose_board0(self, rows: int, columns: int) -> Board:
        pass

    def name(self) -> str:
        pass

    def take_turn(self, current_state: RedactedState) -> Union[Move, Pass]:
        pass

    def win(self, did_win: bool) -> Acknowledgement:
        pass