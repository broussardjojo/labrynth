from player import Player


class APIPlayer:
    def __init__(self, player: Player):
        self.__player = player

    def __call_player_method_with_timeout_protection(self, method_to_call):
        # setup timeout handling
        pass

    def setup(self):
        self.__call_player_method_with_timeout_protection(self.__player.setup)
        pass

    def propose_board0(self):
        pass

    def name(self):
        pass

    def take_turn(self):
        pass

    def won(self):
        pass
