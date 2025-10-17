import tkinter as tk
from tkinter import Tk, filedialog
from pdf_editor import *
from PIL import Image, ImageTk
from dataclasses import dataclass


#Main window class
class App(Tk):

    def __init__(self):
        super().__init__()
        self.resizable(width=False, height=False)
        self.title("PDF Editor")

        self._buttons_frame = tk.Frame(self)
        tk.Button(self._buttons_frame, text="Load PDF", command=self.load_pdf).grid(column=0, row=0)
        tk.Button(self._buttons_frame, text="Remove last selection", command=self.undo_rectangle).grid(column=1, row=0)
        tk.Button(self._buttons_frame, text="Save PDF", command=self.commit_and_save_pdf).grid(column=2, row=0)
        tk.Label(self._buttons_frame, text="Add checkbox:").grid(column=3, row=0)
        self._add_checkbox = tk.IntVar()
        tk.Checkbutton(self._buttons_frame, variable=self._add_checkbox).grid(column=4, row=0)
        self._buttons_frame.pack(side="top")

        self._canvas = None

        #starting positions on click + mouse drag
        self._start_x = None
        self._start_y = None

        self._temp_rectangle = None
        self._canvas_rectangles = []

        self._pdf_file_path = None
        self._pdf_image = None

    @dataclass
    class InputField:
        id: int
        # classic textfield = True
        is_checkbox: bool

    def load_pdf(self) -> None:
        self._pdf_file_path = filedialog.askopenfilename(filetypes=[(".pdf", ".pdf")])

        if self._pdf_file_path:
            page_size = PDFEditor.load_pdf(file_path=self._pdf_file_path)
            pdf_pixmap = PDFEditor.pdf_page_to_pixmap()
            pdf_image = Image.frombytes("RGB", (pdf_pixmap.width, pdf_pixmap.height), pdf_pixmap.samples)
            resized_image = pdf_image.resize((int(page_size.width), int(page_size.height)), Image.Resampling.LANCZOS)

            self._pdf_image = ImageTk.PhotoImage(resized_image)
            self.create_canvas(page_size.width, page_size.height)

    def create_canvas(self, width: int, height: int) -> None:
        if self._canvas:
            self._canvas.destroy()
        self._canvas = tk.Canvas(self, bg="gray75", width=width, height=height)
        self._canvas.create_image(width / 2, height / 2, image=self._pdf_image, anchor=tk.CENTER)
        self._canvas.bind("<Button-1>", self.on_mouse_click)
        self._canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self._canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self._canvas.pack(fill="both", expand=True)

    def on_mouse_click(self, event: tk.Event) -> None:
        self._start_x = event.x
        self._start_y = event.y

    def on_mouse_drag(self, event: tk.Event) -> None:
        if self._temp_rectangle:
            self._canvas.delete(self._temp_rectangle)

        self._temp_rectangle = self._canvas.create_rectangle(
            self._start_x,
            self._start_y,
            event.x,
            event.y,
            width=1,
            outline="#99ad95"
        )

    def on_mouse_release(self, event: tk.Event) -> None:
        self._canvas.delete(self._temp_rectangle)

        color = "#0362fc" if self._add_checkbox.get() else "#32c215"
        self._canvas_rectangles.append(
            self.InputField(
                self._canvas.create_rectangle(
                    self._start_x,
                    self._start_y,
                    event.x,
                    event.y,
                    outline=color,
                    width=2
                ), bool(self._add_checkbox.get())))

    def undo_rectangle(self) -> None:
        if self._canvas_rectangles:
            rectangle_to_remove = self._canvas_rectangles.pop().id
            self._canvas.delete(rectangle_to_remove)
            PDFEditor.remove_widget(str(rectangle_to_remove))

    def commit_and_save_pdf(self) -> None:

        if self._canvas_rectangles:
            for rectangle in self._canvas_rectangles:
                rectangle_coordinates = self._canvas.coords(rectangle.id)
                PDFEditor.create_widget(rectangle_coordinates, str(rectangle.id), rectangle.is_checkbox)
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[(".pdf", ".pdf")])
            if save_path:
                PDFEditor.save_pdf(save_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
