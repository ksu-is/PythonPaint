import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw
import copy

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Program")

        self.canvas_width = 800
        self.canvas_height = 600

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.current_color = "black"
        self.current_tool = "pen"
        self.last_x, self.last_y = None, None
        self.temp_line = None
        self.temp_rect = None
        self.temp_oval = None
        self.drawing = False

        self.history = []  # Stack for undo
        self.redo_history = []  # Stack for redo

        self.brush_size = 3  # Default brush size

        self.create_toolbar()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        # Color button
        color_button = tk.Button(toolbar, text="Color", command=self.choose_color)
        color_button.pack(side=tk.LEFT)

        # Tool buttons
        pen_button = tk.Button(toolbar, text="Pen", command=self.set_pen_tool)
        pen_button.pack(side=tk.LEFT)

        line_button = tk.Button(toolbar, text="Line", command=self.set_line_tool)
        line_button.pack(side=tk.LEFT)

        rect_button = tk.Button(toolbar, text="Rectangle", command=self.set_rect_tool)
        rect_button.pack(side=tk.LEFT)

        oval_button = tk.Button(toolbar, text="Oval", command=self.set_oval_tool)
        oval_button.pack(side=tk.LEFT)

        eraser_button = tk.Button(toolbar, text="Eraser", command=self.set_eraser_tool)
        eraser_button.pack(side=tk.LEFT)

        fill_button = tk.Button(toolbar, text="Fill", command=self.fill_tool)
        fill_button.pack(side=tk.LEFT)

        clear_button = tk.Button(toolbar, text="Clear", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT)

        save_button = tk.Button(toolbar, text="Save", command=self.save_image)
        save_button.pack(side=tk.LEFT)

        open_button = tk.Button(toolbar, text="Open", command=self.open_image)
        open_button.pack(side=tk.LEFT)

        # Undo/Redo buttons
        undo_button = tk.Button(toolbar, text="Undo", command=self.undo)
        undo_button.pack(side=tk.LEFT)

        redo_button = tk.Button(toolbar, text="Redo", command=self.redo)
        redo_button.pack(side=tk.LEFT)

        # Brush size slider
        brush_label = tk.Label(toolbar, text="Brush Size:")
        brush_label.pack(side=tk.LEFT)

        self.brush_size_slider = tk.Scale(toolbar, from_=1, to_=20, orient=tk.HORIZONTAL, command=self.change_brush_size)
        self.brush_size_slider.set(self.brush_size)  # Set initial brush size
        self.brush_size_slider.pack(side=tk.LEFT)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def set_pen_tool(self):
        self.current_tool = "pen"

    def set_line_tool(self):
        self.current_tool = "line"

    def set_rect_tool(self):
        self.current_tool = "rectangle"

    def set_oval_tool(self):
        self.current_tool = "oval"

    def set_eraser_tool(self):
        self.current_tool = "eraser"

    def fill_tool(self):
        self.current_tool = "fill"
        self.flood_fill(self.last_x, self.last_y, self.current_color)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.history.clear()  # Clear history after clearing canvas

    def save_image(self):
        self.image.save("drawing.png")

    def open_image(self):
        pass  # Implement open image functionality here (optional)

    def flood_fill(self, x, y, color):
        target_color = self.image.getpixel((x, y))
        if target_color == color:
            return
        self._flood_fill(x, y, target_color, color)

    def _flood_fill(self, x, y, target_color, color):
        color_rgb = self.hex_to_rgb(color)

        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return
        if self.image.getpixel((x, y)) != target_color:
            return
        self.image.putpixel((x, y), color_rgb)
        self.canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline=color)
        self._flood_fill(x + 1, y, target_color, color)
        self._flood_fill(x - 1, y, target_color, color)
        self._flood_fill(x, y + 1, target_color, color)
        self._flood_fill(x, y - 1, target_color, color)

    def hex_to_rgb(self, hex_color):
        """Convert hex color string to an RGB tuple."""
        if hex_color[0] == '#':
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def on_click(self, event):
        self.last_x, self.last_y = event.x, event.y
        if self.current_tool == "pen" or self.current_tool == "eraser":
            self.drawing = True
        elif self.current_tool == "fill":
            self.flood_fill(event.x, event.y, self.current_color)

    def on_drag(self, event):
        x, y = event.x, event.y

        if self.current_tool == "pen" and self.drawing:
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.last_x, self.last_y = x, y

        elif self.current_tool == "eraser" and self.drawing:
            self.erase(x, y)

        elif self.current_tool == "line":
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            self.temp_line = self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
        elif self.current_tool == "rectangle":
            if self.temp_rect:
                self.canvas.delete(self.temp_rect)
            self.temp_rect = self.canvas.create_rectangle(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)
        elif self.current_tool == "oval":
            if self.temp_oval:
                self.canvas.delete(self.temp_oval)
            self.temp_oval = self.canvas.create_oval(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)

    def on_release(self, event):
        x, y = event.x, event.y

        if self.current_tool == "pen" and self.drawing:
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.drawing = False
            self.save_state()

        elif self.current_tool == "eraser" and self.drawing:
            self.erase(x, y)
            self.drawing = False
            self.save_state()

        elif self.current_tool == "line":
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.temp_line = None
            self.save_state()
        elif self.current_tool == "rectangle":
            self.canvas.create_rectangle(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)
            self.draw.rectangle([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_rect = None
            self.save_state()
        elif self.current_tool == "oval":
            self.canvas.create_oval(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)
            self.draw.ellipse([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_oval = None
            self.save_state()

    def erase(self, x, y):
        self.draw.line([x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size], fill="white", width=self.brush_size * 2)
        self.canvas.create_line(x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size, fill="white", width=self.brush_size * 2)

    def save_state(self):
        """Save the current image state to history for undo."""
        self.history.append(copy.deepcopy(self.image))
        self.redo_history.clear()  # Clear redo history after a new action

    def undo(self):
        """Undo the last action."""
        if self.history:
            self.redo_history.append(copy.deepcopy(self.image))
            self.image = self.history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def redo(self):
        """Redo the last undone action."""
        if self.redo_history:
            self.history.append(copy.deepcopy(self.image))
            self.image = self.redo_history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def update_canvas(self):
        """Redraw the canvas after undo/redo."""
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.get_image_for_canvas())

    def get_image_for_canvas(self):
        """Convert the image to a format that can be displayed on canvas."""
        return ImageTk.PhotoImage(self.image)

    def change_brush_size(self, value):
        """Change brush size based on the slider value."""
        self.brush_size = int(value)


def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
