import tkinter as tk
from tkinter import colorchooser, simpledialog, font
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

        self.history = []
        self.redo_history = []
        self.brush_size = 3

        self.polygon_points = []
        self.text_font = "Arial"
        self.text_size = 20

        self.create_toolbar()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        tk.Button(toolbar, text="Color", command=self.choose_color).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Pen", command=lambda: self.set_tool("pen")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Line", command=lambda: self.set_tool("line")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Rectangle", command=lambda: self.set_tool("rectangle")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Oval", command=lambda: self.set_tool("oval")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Eraser", command=lambda: self.set_tool("eraser")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Fill", command=lambda: self.set_tool("fill")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Polygon", command=lambda: self.set_tool("polygon")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Text", command=lambda: self.set_tool("text")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Redo", command=self.redo).pack(side=tk.LEFT)

        tk.Label(toolbar, text="Brush Size:").pack(side=tk.LEFT)
        self.brush_size_slider = tk.Scale(toolbar, from_=1, to=20, orient=tk.HORIZONTAL, command=self.change_brush_size)
        self.brush_size_slider.set(self.brush_size)
        self.brush_size_slider.pack(side=tk.LEFT)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def set_tool(self, tool):
        self.current_tool = tool
        if tool != "polygon":
            self.polygon_points.clear()

    def clear_canvas(self):
        self.save_state()
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self):
        self.image.save("drawing.png")

    def flood_fill(self, x, y, color):
        try:
            target_color = self.image.getpixel((x, y))
        except IndexError:
            return
        if target_color == self.hex_to_rgb(color):
            return
        self.save_state()
        self._flood_fill(x, y, target_color, self.hex_to_rgb(color))

    def _flood_fill(self, x, y, target_color, color):
        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return
        if self.image.getpixel((x, y)) != target_color:
            return
        self.image.putpixel((x, y), color)
        self.canvas.create_rectangle(x, y, x+1, y+1, fill=self.rgb_to_hex(color), outline="")
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            self._flood_fill(x+dx, y+dy, target_color, color)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def on_click(self, event):
        self.last_x, self.last_y = event.x, event.y
        if self.current_tool in ["pen", "eraser", "line", "rectangle", "oval", "fill"]:
            self.save_state()
        if self.current_tool == "pen" or self.current_tool == "eraser":
            self.drawing = True
        elif self.current_tool == "fill":
            self.flood_fill(event.x, event.y, self.current_color)
        elif self.current_tool == "polygon":
            self.polygon_points.append((event.x, event.y))
            if len(self.polygon_points) > 1:
                self.canvas.create_line(self.polygon_points[-2], self.polygon_points[-1], fill=self.current_color)
        elif self.current_tool == "text":
            text = simpledialog.askstring("Text Input", "Enter text:")
            if text:
                self.save_state()
                font_style = ImageFont.truetype("arial.ttf", self.text_size)
                self.draw.text((event.x, event.y), text, fill=self.current_color, font=font_style)
                self.update_canvas()

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
            self.drawing = False
        elif self.current_tool == "eraser" and self.drawing:
            self.erase(x, y)
            self.drawing = False
        elif self.current_tool == "line":
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.temp_line = None
        elif self.current_tool == "rectangle":
            self.draw.rectangle([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_rect = None
        elif self.current_tool == "oval":
            self.draw.ellipse([self.last_x, self.last_y, x, y], outline=self.current_color, width=self.brush_size)
            self.temp_oval = None

    def erase(self, x, y):
        self.draw.line([x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size], fill="white", width=self.brush_size * 2)
        self.canvas.create_line(x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size, fill="white", width=self.brush_size * 2)

    def save_state(self):
        self.history.append(copy.deepcopy(self.image))
        self.redo_history.clear()

    def undo(self):
        if self.history:
            self.redo_history.append(copy.deepcopy(self.image))
            self.image = self.history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def redo(self):
        if self.redo_history:
            self.history.append(copy.deepcopy(self.image))
            self.image = self.redo_history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas_image = self.get_image_for_canvas()
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)

    def get_image_for_canvas(self):
        return ImageTk.PhotoImage(self.image)

    def change_brush_size(self, value):
        self.brush_size = int(value)


def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
