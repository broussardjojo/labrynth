import io
import json
import tkinter.constants
from collections import deque
from enum import Enum
from tkinter import Canvas, Tk, Button, filedialog
from typing import Deque, Dict, Union

from PIL import Image, ImageTk
from typing_extensions import Literal, assert_never

from ..Common.player_details import PlayerDetails
from ..Common.direction import Direction
from ..Common.gem import Gem
from ..Common.position import Position
from ..Common.state import State
from ..Common.tile import Tile
from ..JSON.serializers import state_to_json


class DisplayStageTag(Enum):
    """
    One of three possible stages for the GUI (PRE_GAME, MID_GAME, POST_GAME)
    """
    PRE_GAME = 0
    MID_GAME = 1
    POST_GAME = 2


class PreGameDisplayStage:
    """
    Represents the stage in which the observer has not yet received a game state
    """
    kind: Literal[DisplayStageTag.PRE_GAME] = DisplayStageTag.PRE_GAME


class MidGameDisplayStage:
    """
    Represents the stage in which the observer has received at least 1 game state, and the user
    is not finished clicking through them
    """
    kind: Literal[DisplayStageTag.MID_GAME] = DisplayStageTag.MID_GAME
    index: int

    def __init__(self, index: int):
        self.index = index


class PostGameDisplayStage:
    """
    Represents the stage in which the observer received all game state, and the user has clicked
    through all of them
    """
    kind: Literal[DisplayStageTag.POST_GAME] = DisplayStageTag.POST_GAME


DisplayStage = Union[PreGameDisplayStage, MidGameDisplayStage, PostGameDisplayStage]


class Observer:
    """
    Represents an Observer for a game of Labyrinth. An observer can display a given State of the game.
    """
    TILE_CANVAS_DIM = 80
    TILE_CONNECTOR_LINEWIDTH = 4
    BUTTON_CANVAS_HEIGHT = 20
    BUTTON_CANVAS_WIDTH = 60
    GAME_OVER_CANVAS_DIM = 400
    HOME_SIZE = 30
    AVATAR_SIZE = 30
    GEM_PADDING = 10

    __window: Tk
    __is_gui_destroyed: bool
    __gem_cache: Dict[Gem, ImageTk.PhotoImage]
    __list_of_states: Deque[State]
    __display_stage: DisplayStage
    __is_current_state_drawn: bool
    __is_game_over: bool
    # Represents the column to the right of the last board column
    __button_column: int

    def __init__(self):
        """
        Creates an instance of an Observer
        """
        self.__window = Tk()
        self.__is_gui_destroyed = False
        self.__window.protocol("WM_DELETE_WINDOW", self.__quit)
        self.__gem_cache = {}
        self.__list_of_states = deque()
        self.__display_stage = PreGameDisplayStage()
        self.__is_current_state_drawn = False
        self.__is_game_over = False
        self.__button_column = -1

    def receive_new_state(self, next_state: State) -> None:
        """
        Takes in a State to be observed.
        :param next_state: a State representing the state of the game to be observed
        :return: None
        """
        self.__list_of_states.append(next_state)
        if len(self.__list_of_states) == 1:
            self.__display_stage = MidGameDisplayStage(0)

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
        if self.__display_stage.kind is DisplayStageTag.MID_GAME:
            index = self.__display_stage.index
            if index < len(self.__list_of_states) - 1:
                self.__set_display_stage(MidGameDisplayStage(index + 1))
            elif self.__is_game_over:
                self.__set_display_stage(PostGameDisplayStage())

    def __set_display_stage(self, display_stage: DisplayStage) -> None:
        """
        Sets the __display_stage field, and informs the main drawing loop to re-render the state on the next pass
        :param display_stage: A {PreGame|MidGame|PostGame}DisplayStage
        :return: None
        """
        self.__is_current_state_drawn = False
        self.__display_stage = display_stage

    def __save(self) -> None:
        """
        Saves the current State of the game as a JSON string into a created txt file in the location chosen by the user.
        :return: None
        """
        if self.__display_stage.kind is not DisplayStageTag.MID_GAME:
            return
        current_state = self.__list_of_states[self.__display_stage.index]
        output_file = filedialog.asksaveasfile("wb", initialdir="/", title="Select a File",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
        if output_file is None:
            # User cancelled
            return
        serialized_state = state_to_json(current_state)
        jsonified_state = json.dumps(serialized_state, ensure_ascii=False)
        text_fileobj = io.TextIOWrapper(output_file, encoding="utf-8")
        text_fileobj.write(jsonified_state)

    def __quit(self) -> None:
        """
        Sets the __is_gui_destroyed flag, so that display_gui won't update a closed window
        :return: None
        """
        self.__is_gui_destroyed = True

    def display_gui(self) -> bool:
        """
        Updates the window to display the latest state. Should be called in a loop - failing to call this method
        often enough could result in user input being ignored when Tk runs out of space to hold pending events
        :return: True if the app should continue to send updates, False otherwise (meaning the user has quit)
        """
        if self.__is_gui_destroyed:
            return False
        self.__draw_current_state()
        self.__window.update()
        return True

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
        if self.__is_current_state_drawn:
            # State has already been drawn
            return
        if self.__display_stage.kind is DisplayStageTag.PRE_GAME:
            pass
        elif self.__display_stage.kind is DisplayStageTag.MID_GAME:
            current_state = self.__list_of_states[self.__display_stage.index]
            button_column = current_state.get_board().get_width()
            self.__draw_basic_board(current_state)
            self.__add_buttons(button_column)
            self.__is_current_state_drawn = True
        elif self.__display_stage.kind is DisplayStageTag.POST_GAME:
            assert self.__is_game_over
            self.__draw_game_over_screen()
        else:
            assert_never(self.__display_stage)

    def __draw_basic_board(self, current_state: State) -> None:
        """
        Draws a state of the game as a board with its tile grid, the players' current positions, and player homes
        :return: None
        """
        current_board = current_state.get_board()
        current_tile_grid = current_board.get_tile_grid()
        for row, tiles in enumerate(current_tile_grid):
            for col, tile in enumerate(tiles):
                drawn_tile = self.__draw_tile(tile)
                homes_added = self.__add_home_at(current_state, row, col, drawn_tile)
                homes_and_avatars_added = self.__add_avatars_at(current_state, row, col, homes_added)
                homes_and_avatars_added.grid(row=row, column=col)
        self.__draw_spare_tile(current_board.get_next_tile(), current_board.get_height())

    def __draw_spare_tile(self, spare_tile: Tile, board_height: int) -> None:
        """
        Draws the given tile in the row below the given int, which represents the board size of the Board the given
        spare tile belongs to
        :param spare_tile: the spare tile being drawn
        :param board_height: an int which represents the height of the Board the given spare tile belongs to
        :return: None
        """
        spare_tile_canvas = self.__draw_tile(spare_tile)
        spare_tile_canvas.grid(row=board_height, column=0)

    def __draw_tile(self, tile_to_draw: Tile) -> Canvas:
        canvas = Canvas(width=self.TILE_CANVAS_DIM, height=self.TILE_CANVAS_DIM, bd=0, highlightthickness=1)
        canvas.create_rectangle(0, 0, self.TILE_CANVAS_DIM, self.TILE_CANVAS_DIM, fill="lemon chiffon",
                                outline="lemon chiffon")
        self.__draw_shape_from_tile(tile_to_draw, canvas)
        self.__draw_gems_from_tile(tile_to_draw, canvas)
        return canvas

    def __draw_shape_from_tile(self, tile_to_draw: Tile, canvas: Canvas) -> None:
        """
        Draws the shape of the given tile on the canvas
        :param tile_to_draw: the Tile whose Shape is being drawn
        :param canvas: the Canvas on which to draw
        :return: None
        """
        x_left, x_center, x_right = 0, self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM
        y_top, y_center, y_bottom = 0, self.TILE_CANVAS_DIM / 2, self.TILE_CANVAS_DIM
        if tile_to_draw.has_path(Direction.UP):
            canvas.create_line(x_center, y_center, x_center, y_top, width=self.TILE_CONNECTOR_LINEWIDTH)
        if tile_to_draw.has_path(Direction.RIGHT):
            canvas.create_line(x_center, y_center, x_right, y_center, width=self.TILE_CONNECTOR_LINEWIDTH)
        if tile_to_draw.has_path(Direction.DOWN):
            canvas.create_line(x_center, y_center, x_center, y_bottom, width=self.TILE_CONNECTOR_LINEWIDTH)
        if tile_to_draw.has_path(Direction.LEFT):
            canvas.create_line(x_center, y_center, x_left, y_center, width=self.TILE_CONNECTOR_LINEWIDTH)

    def __get_gem_image(self, gem: Gem) -> ImageTk.PhotoImage:
        if gem in self.__gem_cache:
            return self.__gem_cache[gem]
        desired_image_dim = round((self.TILE_CANVAS_DIM / 2) - 2 * self.GEM_PADDING)
        image = Image.open(gem.get_gem_filepath())
        image.thumbnail((desired_image_dim, desired_image_dim))
        image_tk = ImageTk.PhotoImage(image)
        self.__gem_cache[gem] = image_tk
        return image_tk

    def __draw_gems_from_tile(self, tile_to_draw: Tile, canvas: Canvas) -> None:
        """
        Draws the gems of the given tile on the canvas
        :param tile_to_draw: the Tile whose Gems are being drawn
        :param canvas: the Canvas on which to draw
        :return: None
        """
        gem1, gem2 = tile_to_draw.get_gems()
        padded_right_and_bottom = self.TILE_CANVAS_DIM - self.GEM_PADDING
        for gem, layout_info in [
            (gem1, (self.GEM_PADDING, self.GEM_PADDING, tkinter.constants.NW)),
            (gem2, (padded_right_and_bottom, padded_right_and_bottom, tkinter.constants.SE)),
        ]:
            x, y, anchor = layout_info
            canvas.create_image(x, y, anchor=anchor, image=self.__get_gem_image(gem))

    def __add_home_at(self, current_state: State, row: int, col: int, drawn_tile: Canvas) -> Canvas:
        """
        Draws a player home on the given drawn_tile Canvas if a player has a home at the given row, col position on the
        current state's board
        :param current_state: the current State of the game
        :param row: an int representing the row on the state's board being checked for a players home
        :param col: an int representing the column on the state's board being checked for a players home
        :param drawn_tile: a Canvas representing a drawn tile on the state's board
        :return: the given drawn Tile with a player's home on it if there is one, otherwise just the given drawn tile
        """
        players = current_state.get_players()
        for player in players:
            if player.get_home_position() == Position(row, col):
                return self.__add_home_to_canvas(drawn_tile, player)
        return drawn_tile

    def __add_home_to_canvas(self, drawn_tile: Canvas, player: PlayerDetails) -> Canvas:
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

    def __add_avatars_at(self, current_state: State, row: int, col: int, drawn_tile: Canvas) -> Canvas:
        """
        Draws a player's current position on the given drawn_tile Canvas if a player has a current position at the given
        row, col position on the current state's board
        :param current_state: the current State of the game
        :param row: an int representing the row on the state's board being checked for a players current position
        :param col: an int representing the column on the state's board being checked for a players current position
        :param drawn_tile: a Canvas representing a drawn tile on the state's board
        :return: the given drawn Tile with a player's avatar on it if there is a player on it, otherwise just the given
        drawn tile
        """
        players = current_state.get_players()
        offset = 0
        for player in players:
            if player.get_current_position() == Position(row, col):
                drawn_tile = self.__add_avatar_to_canvas(drawn_tile, player, offset)
                offset += 5
        return drawn_tile

    def __add_avatar_to_canvas(self, drawn_tile: Canvas, player: PlayerDetails, offset: int) -> Canvas:
        """
        Draws the given player's avatar on the given canvas
        # TODO: take in an index and total number of players, then compute a non-overlapping area to draw in
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
        if self.__button_column == button_column:
            # Buttons have already been drawn in the right place
            return
        self.__button_column = button_column
        next_btn = Button(self.__window,
                          text="Next", command=self.__next)
        next_btn.grid(row=0, column=button_column)
        save_btn = Button(self.__window,
                          text="Save", command=self.__save, state=("normal" if self.__list_of_states else "disabled"))
        save_btn.grid(row=1, column=button_column)
