import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw
import copy

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Program")

        # Canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 600

        # Create the canvas widget
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # Create a new image object (for saving the drawing)
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)  # Used for drawing on the image

        # Default color and tool settings
        self.current_color = "black"
        self.current_tool = "pen"
        self.last_x, self.last_y = None, None  # Store last coordinates for drawing lines
        self.temp_line = None  # Temporary line object for live preview
        self.temp_rect = None  # Temporary rectangle object for live preview
        self.temp_oval = None  # Temporary oval object for live preview
        self.drawing = False  # Flag to track if the user is drawing

        # Undo/Redo history stacks
        self.history = []  # Stores the history of images for undo
        self.redo_history = []  # Stores the history of undone actions for redo

        # Default brush size
        self.brush_size = 3

        # Create the toolbar with all the buttons and controls
        self.create_toolbar()

        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.on_click)  # Mouse click event
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Mouse drag event
        self.canvas.bind("<ButtonRelease-1>", self.on_release)  # Mouse release event

    def create_toolbar(self):
        """Creates the toolbar at the top of the window with buttons for tools and color selection."""
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        # Color selection button
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

        # Slider for adjusting the brush size (from 1 to 20)
        self.brush_size_slider = tk.Scale(toolbar, from_=1, to_=20, orient=tk.HORIZONTAL, command=self.change_brush_size)
        self.brush_size_slider.set(self.brush_size)  # Set the initial brush size
        self.brush_size_slider.pack(side=tk.LEFT)

    def choose_color(self):
        """Open a color chooser dialog to select a color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def set_pen_tool(self):
        """Set the current tool to 'pen'."""
        self.current_tool = "pen"

    def set_line_tool(self):
        """Set the current tool to 'line'."""
        self.current_tool = "line"

    def set_rect_tool(self):
        """Set the current tool to 'rectangle'."""
        self.current_tool = "rectangle"

    def set_oval_tool(self):
        """Set the current tool to 'oval'."""
        self.current_tool = "oval"

    def set_eraser_tool(self):
        """Set the current tool to 'eraser'."""
        self.current_tool = "eraser"

    def fill_tool(self):
        """Set the current tool to 'fill' (flood fill)."""
        self.current_tool = "fill"
        self.flood_fill(self.last_x, self.last_y, self.current_color)

    def clear_canvas(self):
        """Clear the canvas and reset the image."""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.history.clear()  # Clear history after clearing canvas

    def save_image(self):
        """Save the current drawing as a PNG file."""
        self.image.save("drawing.png")

    def open_image(self):
        """Optional: Open an image (not implemented)."""
        pass

    def flood_fill(self, x, y, color):
        """Flood fill (bucket fill) function to fill an area with the selected color."""
        target_color = self.image.getpixel((x, y))
        if target_color == color:
            return
        self._flood_fill(x, y, target_color, color)

    def _flood_fill(self, x, y, target_color, color):
        """Recursive function to fill an area with the selected color."""
        color_rgb = self.hex_to_rgb(color)

        # Ensure we're within the canvas bounds
        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return
        # Check if the pixel color matches the target color
        if self.image.getpixel((x, y)) != target_color:
            return
        # Set the pixel color to the new color
        self.image.putpixel((x, y), color_rgb)
        self.canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline=color)

        # Recursively fill neighboring pixels
        self._flood_fill(x + 1, y, target_color, color)
        self._flood_fill(x - 1, y, target_color, color)
        self._flood_fill(x, y + 1, target_color, color)
        self._flood_fill(x, y - 1, target_color, color)

    def hex_to_rgb(self, hex_color):
        """Convert a hex color string (e.g., '#FF0000') to an RGB tuple."""
        if hex_color[0] == '#':
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def on_click(self, event):
        """Called when the user clicks on the canvas."""
        self.last_x, self.last_y = event.x, event.y
        if self.current_tool == "pen" or self.current_tool == "eraser":
            self.drawing = True
        elif self.current_tool == "fill":
            self.flood_fill(event.x, event.y, self.current_color)

    def on_drag(self, event):
        """Called when the user drags the mouse on the canvas (for drawing)."""
        x, y = event.x, event.y

        if self.current_tool == "pen" and self.drawing:
            # Draw a line from the last position to the current position
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.last_x, self.last_y = x, y

        elif self.current_tool == "eraser" and self.drawing:
            # Erase a portion of the image (draw white lines)
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
        """Called when the user releases the mouse button after drawing."""
        x, y = event.x, event.y

        if self.current_tool == "pen" and self.drawing:
            # Finalize the pen drawing
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.drawing = False

        elif self.current_tool == "eraser" and self.drawing:
            # Finalize the eraser action
            self.erase(x, y)
            self.drawing = False

        elif self.current_tool == "line":
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.temp_line = None
        elif self.current_tool == "rectangle":
            self.canvas.create_rectangle(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)
            self.draw.rectangle([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_rect = None
        elif self.current_tool == "oval":
            self.canvas.create_oval(self.last_x, self.last_y, x, y, outline=self.current_color, width=self.brush_size)
            self.draw.ellipse([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_oval = None

    def erase(self, x, y):
        """Erase a part of the image using the eraser tool."""
        self.draw.line([x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size], fill="white", width=self.brush_size * 2)
        self.canvas.create_line(x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size, fill="white", width=self.brush_size * 2)

    def save_state(self):
        """Save the current state of the image for undo functionality."""
        self.history.append(copy.deepcopy(self.image))
        self.redo_history.clear()  # Clear redo history after new action

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
        """Convert the image to a format that can be displayed on the canvas."""
        return ImageTk.PhotoImage(self.image)

    def change_brush_size(self, value):
        """Change the brush size based on the slider value."""
        self.brush_size = int(value)


def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
