from ..Common.state import State


class Observer:
    def __init__(self):
        self.__list_of_states = []
        self.__current_state_index = 0
        self.__is_game_over = False

    def receive_new_state(self, next_state: State):
        self.__list_of_states.append(next_state)

    def game_is_over(self):
        self.__is_game_over = True

    def __next(self):
        if self.__current_state_index < len(self.__list_of_states) - 1:
            self.__current_state_index += 1
            self.__redraw_view()

    def __redraw_view(self):
        if self.__current_state_index == len(self.__list_of_states) - 1 and self.__is_game_over:
            self.__draw_game_over_screen()
        else:
            self.__draw_current_state()

    def __save(self):
        pass

    def __draw_game_over_screen(self):
        pass

    def __draw_current_state(self):
        pass
