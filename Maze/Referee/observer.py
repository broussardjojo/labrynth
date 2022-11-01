from tkinter import Canvas, Tk, Button
from typing import List
from threading import Thread

from ..Common.position import Position
from ..Common.board import Board
from ..Common.direction import Direction
from ..Common.tile import Tile
from ..Common.state import State


class Observer:
    """
    Represents an Observer for a game of Labyrinth. An observer can display a given State of the game.
    """
    TILE_CANVAS_DIM = 80
    BUTTON_CANVAS_HEIGHT = 20
    BUTTON_CANVAS_WIDTH = 60
    HOME_SIZE = 30
    AVATAR_SIZE = 30

    def __init__(self):
        """
        Creates an instance of an Observer
        """
        self.__list_of_states: List[State] = []
        self.__current_state_index = 0
        self.__is_game_over = False
        self.__window = Tk()
        self.__gem_img_dict = {}

    def receive_new_state(self, next_state: State) -> None:
        """
        Takes in a State to be observed.
        :param next_state: a State representing the state of the game to be observed
        :return: None
        """
        self.__list_of_states.append(next_state)
        if len(self.__list_of_states) == 1:
            self.__redraw_view()

    def game_is_over(self) -> None:
        """
        Declares that the game being observed is over
        :return: None
        """
        self.__is_game_over = True

    def next(self) -> None:
        """
        Shows the next state of the game, if available. If not, shows the most recently observed state of the game.
        :return: None
        """
        if self.__current_state_index < len(self.__list_of_states) - 1:
            self.__current_state_index += 1
        self.__redraw_view()

    def __redraw_view(self) -> None:
        """
        Draws a game over screen if the game is over, else draws the current state of the game
        :return: None
        """
        if self.__current_state_index == len(self.__list_of_states) - 1 and self.__is_game_over:
            self.__draw_game_over_screen()
        else:
            self.__draw_current_state()
        self.__window.mainloop()

    def __save(self):
        pass

    def __draw_game_over_screen(self):
        pass

    def __draw_current_state(self) -> None:
        """
        Draws the current state of the game
        :return: None
        """
        self.__draw_basic_board()
        self.__add_buttons()

    def __draw_basic_board(self) -> None:
        # TODO: draw spare tile???
        """
        Draws a state of the game as a board with its tile grid, the players' current positions, and player homes
        :return: None
        """
        if len(self.__list_of_states) > 0:
            current_state = self.__list_of_states[self.__current_state_index]
            current_board = current_state.get_board()
            current_tile_grid = current_board.get_tile_grid()
            for row in range(len(current_tile_grid)):
                for col in range(len(current_tile_grid[row])):
                    drawn_tile = self.__draw_shape_from_tile(current_tile_grid[row][col])
                    homes_added = self.__add_home_at(row, col, drawn_tile)
                    homes_and_avatars_added = self.__add_avatars_at(row, col, homes_added)
                    homes_and_avatars_added.grid(row=row, column=col)

    def __draw_shape_from_tile(self, tile_to_draw: Tile) -> Canvas:
        """
        Draws the shape of the given tile
        :param tile_to_draw: the Tile whose Shape is being drawn
        :return: a Canvas representing a Tile with its Shape
        """
        canvas = Canvas(width=self.TILE_CANVAS_DIM, height=self.TILE_CANVAS_DIM, bd=0, highlightthickness=1)
        canvas.pack()
        canvas.create_rectangle(0, 0, self.TILE_CANVAS_DIM, self.TILE_CANVAS_DIM, fill="lemon chiffon",
                                outline="lemon chiffon")
        if tile_to_draw.has_path(Direction.Up):
            canvas.create_line(self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2, 0)
        if tile_to_draw.has_path(Direction.Right):
            canvas.create_line(self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM,
                               self.TILE_CANVAS_DIM / 2)
        if tile_to_draw.has_path(Direction.Left):
            canvas.create_line(self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2, 0, self.TILE_CANVAS_DIM / 2)
        if tile_to_draw.has_path(Direction.Down):
            canvas.create_line(self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM / 2,
                               self.TILE_CANVAS_DIM)
        return canvas

    def __add_home_at(self, row, col, drawn_tile) -> Canvas:
        """
        Draws a player home on the given drawn_tile Canvas if a player has a home at the given row, col position on the
        current state's board
        :param row: an int representing the row on the state's board being checked for a players home
        :param col: an int representing the column on the state's board being checked for a players home
        :param drawn_tile: a Canvas representing a drawn tile on the state's board
        :return: the given drawn Tile with a player's home on it if there is one, otherwise just the given drawn tile
        """
        players = self.__list_of_states[self.__current_state_index].get_players()
        for player in players:
            if player.get_home_position() == Position(row, col):
                return self.__add_home_to_canvas(drawn_tile, player)
        return drawn_tile

    def __add_home_to_canvas(self, drawn_tile, player) -> Canvas:
        """
        Draws the given player's home on the given canvas
        :param drawn_tile: a canvas representing a drawing of a tile on the current state's board
        :param player: the player who's home is being drawn on the given canvas
        :return: a canvas with the given player's home drawn on it
        """
        player_color = player.get_color()
        drawn_tile.create_rectangle(0, self.TILE_CANVAS_DIM, self.HOME_SIZE, self.TILE_CANVAS_DIM - self.HOME_SIZE,
                                    fill=player_color, outline=player_color)
        return drawn_tile

    def __add_avatars_at(self, row, col, drawn_tile) -> Canvas:
        """
        Draws a player's current position on the given drawn_tile Canvas if a player has a current position at the given
        row, col position on the current state's board
        :param row: an int representing the row on the state's board being checked for a players current position
        :param col: an int representing the column on the state's board being checked for a players current position
        :param drawn_tile: a Canvas representing a drawn tile on the state's board
        :return: the given drawn Tile with a player's avatar on it if there is a player on it, otherwise just the given
        drawn tile
        """
        players = self.__list_of_states[self.__current_state_index].get_players()
        for player in players:
            if player.get_current_position() == Position(row, col):
                return self.__add_avatar_to_canvas(drawn_tile, player)
        return drawn_tile

    def __add_avatar_to_canvas(self, drawn_tile, player) -> Canvas:
        """
        Draws the given player's avatar on the given canvas
        :param drawn_tile: a canvas representing a drawing of a tile on the current state's board
        :param player: the player who's avatar is being drawn on the given canvas
        :return: a canvas with the given player's avatar drawn on it
        """
        player_color = player.get_color()
        drawn_tile.create_oval(self.TILE_CANVAS_DIM - self.AVATAR_SIZE, self.AVATAR_SIZE,
                               self.TILE_CANVAS_DIM, 0,
                               fill=player_color, outline=player_color)
        return drawn_tile

    def __add_buttons(self) -> None:
        """
        Adds a button for the "self.next" command to a canvas
        :return: None
        """
        canvas = Canvas(height=self.BUTTON_CANVAS_HEIGHT, width=self.BUTTON_CANVAS_WIDTH)
        btn = Button(canvas,
                     text="Next", command=self.next)
        btn.place(x=0, y=0)
        canvas.grid(row=0, column=8)

    def display_gui(self):
        self.__redraw_view()


def perform_task(observer):
    print("here")
    board = Board.from_random_board(seed=9)
    state = State.from_random_state(board)
    state.add_player()
    state.add_player()
    observer.receive_new_state(state)
    board2 = Board.from_random_board(seed=10)
    state2 = State.from_random_state(board2)
    state2.add_player()
    state2.add_player()
    state2.add_player()
    state2.add_player()
    observer.receive_new_state(state2)


if __name__ == "__main__":
    observer2 = Observer()
    thread = Thread(target=perform_task, args=(observer2,))
    thread.start()
    observer2.display_gui()
