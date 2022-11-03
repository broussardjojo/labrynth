from .player import Player


# TODO: implement class

class APIPlayer:
    """
    A class that represents a Player with protected player-referee interactions. Namely, a class where method calls are
    protected from timing out and throwing exceptions.
    """
    def __init__(self, player: Player):
        """
        Creates an instance of an API player with the given Player
        :param player: represents a Player who will have a protected interaction with a referee
        """
        self.__player = player

    def __call_player_method_with_timeout_protection(self, method_to_call):
        """
        Calls the given method while handling a possible timeout exception.
        :param method_to_call: the method being called by this APIPlayer's Player
        :return: Any
        """
        # setup timeout handling
        pass

    def setup(self):
        """
        Calls the player set-up method on this APIPlayer's Player while handling a possible timeout exception
        :return: None
        """
        self.__call_player_method_with_timeout_protection(self.__player.setup)
        pass

    def propose_board0(self):
        """
        Calls the player proposed_board0 method on this APIPlayer's Player while handling a possible timeout exception
        :return: optional Board
        """
        pass

    def name(self):
        """
        Calls the player name method on this APIPlayer's Player while handling a possible timeout exception
        :return: str
        """
        pass

    def take_turn(self):
        """
        Calls the player take_turn method on this APIPlayer's Player while handling a possible timeout exception
        :return: Move
        """
        pass

    def won(self):
        """
        Calls the player won method on this APIPlayer's Player while handling a possible timeout exception
        :return: None
        """
        pass
