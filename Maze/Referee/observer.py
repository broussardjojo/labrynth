import json
from copy import deepcopy
from tkinter import Canvas, Tk, Button, filedialog
from typing import List

from ..Common.position import Position
from ..Common.direction import Direction
from ..Common.tile import Tile
from ..Common.state import State
from ..Common.tileSerializer import get_serialized_tile
from ..Common.boardSerializer import get_serialized_board
from ..Players.moveSerializer import get_serialized_last_action
from ..Players.player import Player
from ..Players.playerSerializer import get_serialized_players


class Observer:
    """
    Represents an Observer for a game of Labyrinth. An observer can display a given State of the game.
    """
    TILE_CANVAS_DIM = 80
    BUTTON_CANVAS_HEIGHT = 20
    BUTTON_CANVAS_WIDTH = 60
    GAME_OVER_CANVAS_DIM = 400
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

    def receive_new_state(self, next_state: State) -> None:
        """
        Takes in a State to be observed.
        :param next_state: a State representing the state of the game to be observed
        :return: None
        """
        self.__list_of_states.append(deepcopy(next_state))

    def set_game_is_over(self) -> None:
        """
        Declares that the game being observed is over
        :return: None
        """
        self.__is_game_over = True

    def __next(self) -> None:
        """
        Shows the next state of the game, if available. If not, shows the most recently observed state of the game.
        :return: None
        """
        if self.__current_state_index < len(self.__list_of_states) - 1:
            self.__current_state_index += 1
            self.__draw_current_state()
        elif self.__is_game_over:
            self.__draw_game_over_screen()

    def __save(self) -> None:
        """
        Saves the current State of the game as a JSON string into a created txt file in the location chosen by the user.
        :return: None
        """
        filename = filedialog.asksaveasfile(initialdir="/", title="Select a File",
                                            filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
        if filename:
            serialized_state = self.__get_serialized_state(self.__list_of_states[self.__current_state_index])
            jsonified_state = json.dumps(serialized_state, ensure_ascii=False)
            filename.write(jsonified_state)

    def __draw_game_over_screen(self) -> None:
        """
        Draws a "game over" screen that lets the observer see that no more States will become available
        :return: None
        """
        canvas = Canvas(width=self.__window.winfo_width(), height=self.__window.winfo_height())
        canvas.create_text(self.__window.winfo_width() / 2, self.__window.winfo_height() / 2,
                           text="Game Over!", font=('Helvetica', '50', 'bold'), fill='black')
        canvas.place(x=0, y=0)

    def __draw_current_state(self) -> None:
        """
        Draws the current state of the game
        :return: None
        """
        self.__draw_basic_board()
        button_column = 0
        if self.__list_of_states:
            button_column = len(self.__list_of_states[0].get_board().get_tile_grid())
        self.__add_buttons(button_column)

    def __draw_basic_board(self) -> None:
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
            self.__draw_spare_tile(current_board.get_next_tile(), len(current_tile_grid))

    def __draw_spare_tile(self, spare_tile: Tile, board_size: int) -> None:
        """
        Draws the given tile in the row below the given int, which represents the board size of the Board the given
        spare tile belongs to
        :param spare_tile: the spare tile being drawn
        :param board_size: an int which represents the dimensions of the board size of the Board the given
        spare tile belongs to
        :return: None
        """
        spare_tile_canvas = self.__draw_shape_from_tile(spare_tile)
        spare_tile_canvas.grid(row=board_size, column=0)

    def __draw_shape_from_tile(self, tile_to_draw: Tile) -> Canvas:
        """
        Draws the shape of the given tile
        :param tile_to_draw: the Tile whose Shape is being drawn
        :return: a Canvas representing a Tile with its Shape
        """
        canvas = Canvas(width=self.TILE_CANVAS_DIM, height=self.TILE_CANVAS_DIM, bd=0, highlightthickness=1)
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

    def __add_home_at(self, row: int, col: int, drawn_tile: Canvas) -> Canvas:
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

    def __add_home_to_canvas(self, drawn_tile: Canvas, player: Player) -> Canvas:
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

    def __add_avatars_at(self, row: int, col: int, drawn_tile: Canvas) -> Canvas:
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
        offset = 0
        for player in players:
            if player.get_current_position() == Position(row, col):
                drawn_tile = self.__add_avatar_to_canvas(drawn_tile, player, offset)
                offset += 5
        return drawn_tile

    def __add_avatar_to_canvas(self, drawn_tile: Canvas, player: Player, offset: int) -> Canvas:
        """
        Draws the given player's avatar on the given canvas
        :param drawn_tile: a canvas representing a drawing of a tile on the current state's board
        :param player: the player who's avatar is being drawn on the given canvas
        :return: a canvas with the given player's avatar drawn on it
        """
        player_color = player.get_color()
        drawn_tile.create_oval(self.TILE_CANVAS_DIM - self.AVATAR_SIZE, self.AVATAR_SIZE + offset,
                               self.TILE_CANVAS_DIM, 0 + offset,
                               fill=player_color, outline=player_color)
        return drawn_tile

    def __add_buttons(self, button_column: int) -> None:
        """
        Adds a button for the "self.next" command to a canvas
        :return: None
        """
        next_btn = Button(self.__window,
                          text="Next", command=self.__next)
        next_btn.grid(row=0, column=button_column)
        save_btn = Button(self.__window,
                          text="Save", command=self.__save, state=("normal" if self.__list_of_states else "disabled"))
        save_btn.grid(row=1, column=button_column)

    def display_gui(self) -> None:
        """
        Displays the current state in a pop-up window
        :return: None
        """
        self.__draw_current_state()
        self.__window.mainloop()

    @staticmethod
    def __get_serialized_state(current_state: State) -> dict:
        """
        Converts information from the given state into a dictionary
        :param current_state: the State whose information is being turned into a dictionary
        :return: a dictionary containing information on the given state including its board, the spare tile, the
        players, and the last action
        """
        state_dict = {'board': get_serialized_board(current_state.get_board()),
                      'spare': get_serialized_tile(current_state.get_board().get_next_tile()),
                      'plmt': get_serialized_players(current_state.get_players()),
                      'last': get_serialized_last_action(current_state.get_all_previous_non_passes())
                      }
        return state_dict
