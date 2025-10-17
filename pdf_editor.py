import fitz
from dataclasses import dataclass


@dataclass
class PDFPage:
    width: int
    height: int


class PDFEditor:
    _pdf_file = None
    _widgets = []
    _file_path = None

    @classmethod
    def load_pdf(cls, file_path: str) -> PDFPage:
        _file_path = file_path
        cls._pdf_file = fitz.open(file_path)

        page = cls._pdf_file[0]
        page_width = page.rect.width
        page_height = page.rect.height

        return PDFPage(page_width, page_height)

    @classmethod
    def create_widget(cls, coordinates: tuple, name: str, checkbox=False):
        page = cls._pdf_file[0]
        #2 = checkbox, 7 = input field
        field_type = 2 if checkbox else 7
        if name not in cls._widgets:
            new_widget = fitz.Widget()
            new_widget.field_name = name
            new_widget.rect = fitz.Rect(coordinates)
            new_widget.field_type = field_type
            page.add_widget(new_widget)
            cls._widgets.append(name)

    @classmethod
    def remove_widget(cls, widget_id):
        page = cls._pdf_file[0]
        widget_to_remove = None
        for widget in page.widgets():
            if widget_id == widget.field_name:
                widget_to_remove = widget
                break
        if widget_to_remove:
            page.delete_widget(widget_to_remove)

    @classmethod
    def save_pdf(cls, path: str) -> None:
        cls._pdf_file.save(path)
        cls._pdf_file.close()
        cls.load_pdf(path)

    @classmethod
    def pdf_page_to_pixmap(cls) -> fitz.Pixmap:
        page = cls._pdf_file[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        return pix
