from tkinter import Tk, Canvas
import sys

CANVAS_DIM = 100


# draws the provided shape at the provided grid position in the middle of the canvas

def draw_shape(col, row, character):
    canvas = Canvas(width=CANVAS_DIM, height=CANVAS_DIM)
    if character == "┌":
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM, CANVAS_DIM / 2)
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM)
    elif character == "└":
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM, CANVAS_DIM / 2)
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM / 2, 0)
    elif character == "┘":
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, 0, CANVAS_DIM / 2)
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM / 2, 0)
    elif character == "┐":
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, 0, CANVAS_DIM / 2)
        canvas.create_line(CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM / 2, CANVAS_DIM)
    canvas.grid(column=col, row=row)


# returns the coordinates of the mouse click relative to the coordinates on each canvas in the grid

def mouse_click(event):
    print("Mouse position: (%s %s)" % (event.x, event.y))
    return


if __name__ == "__main__":
    window = Tk()
    stdin = sys.stdin.read()
    within_string = False
    row_counter = 0
    col_counter = 0
    for input_character in stdin:
        if input_character == "\"":
            if within_string:
                row_counter += 1
                col_counter = 0
            within_string = not within_string
        if within_string:
            draw_shape(col_counter, row_counter, input_character)
            col_counter += 1
    window.bind("<Button-1>", mouse_click)
    window.mainloop()
