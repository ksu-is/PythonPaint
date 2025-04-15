import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import io

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Program")

        # Initialize canvas size
        self.canvas_width = 600
        self.canvas_height = 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()

        # Initialize Image for drawing
        self.image = Image.new('RGB', (self.canvas_width, self.canvas_height), color='white')
        self.draw = ImageDraw.Draw(self.image)

        # Variables
        self.current_color = 'black'
        self.brush_size = 3
        self.current_tool = 'brush'  # Can be 'brush', 'eraser', 'line', 'rectangle', 'oval'
        self.undo_stack = []
        self.redo_stack = []

        # Binding events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset_position)

        # Toolbar for tools and options
        self.toolbar_frame = tk.Frame(root)
        self.toolbar_frame.pack()

        self.color_button = tk.Button(self.toolbar_frame, text="Color", command=self.choose_color)
        self.color_button.grid(row=0, column=0)

        self.clear_button = tk.Button(self.toolbar_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.grid(row=0, column=1)

        self.save_button = tk.Button(self.toolbar_frame, text="Save", command=self.save_image)
        self.save_button.grid(row=0, column=2)

        self.load_button = tk.Button(self.toolbar_frame, text="Load", command=self.load_image)
        self.load_button.grid(row=0, column=3)

        self.eraser_button = tk.Button(self.toolbar_frame, text="Eraser", command=self.use_eraser)
        self.eraser_button.grid(row=0, column=4)

        self.undo_button = tk.Button(self.toolbar_frame, text="Undo", command=self.undo)
        self.undo_button.grid(row=0, column=5)

        self.redo_button = tk.Button(self.toolbar_frame, text="Redo", command=self.redo)
        self.redo_button.grid(row=0, column=6)

        # Brush size selector
        self.brush_size_label = tk.Label(self.toolbar_frame, text="Brush Size:")
        self.brush_size_label.grid(row=1, column=0)

        self.brush_size_scale = tk.Scale(self.toolbar_frame, from_=1, to=10, orient='horizontal', command=self.update_brush_size)
        self.brush_size_scale.set(self.brush_size)
        self.brush_size_scale.grid(row=1, column=1, columnspan=2)

        self.line_button = tk.Button(self.toolbar_frame, text="Line", command=self.draw_line)
        self.line_button.grid(row=1, column=3)

        self.rect_button = tk.Button(self.toolbar_frame, text="Rectangle", command=self.draw_rectangle)
        self.rect_button.grid(row=1, column=4)

        self.oval_button = tk.Button(self.toolbar_frame, text="Oval", command=self.draw_oval)
        self.oval_button.grid(row=1, column=5)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new('RGB', (self.canvas_width, self.canvas_height), color='white')
        self.draw = ImageDraw.Draw(self.image)
        self.save_to_undo_stack()

    def paint(self, event):
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)

        if self.current_tool == 'brush':
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.current_color, outline=self.current_color)
            self.draw.line([x1, y1, x2, y2], fill=self.current_color, width=self.brush_size)

    def reset_position(self, event):
        self.save_to_undo_stack()

    def use_eraser(self):
        self.current_tool = 'eraser'
        self.current_color = 'white'

    def update_brush_size(self, val):
        self.brush_size = int(val)

    def draw_line(self):
        self.current_tool = 'line'

    def draw_rectangle(self):
        self.current_tool = 'rectangle'

    def draw_oval(self):
        self.current_tool = 'oval'

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("Success", f"Image saved to {file_path}")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            loaded_image = Image.open(file_path)
            self.image.paste(loaded_image)
            self.canvas.create_image(0, 0, anchor="nw", image=ImageTk.PhotoImage(loaded_image))
            self.save_to_undo_stack()

    def save_to_undo_stack(self):
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 10:  # Limit stack size to avoid memory overflow
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            image = self.undo_stack.pop()
            self.redo_stack.append(self.image)
            self.image = image
            self.update_canvas()

    def redo(self):
        if self.redo_stack:
            image = self.redo_stack.pop()
            self.undo_stack.append(self.image)
            self.image = image
            self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=ImageTk.PhotoImage(self.image))

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
