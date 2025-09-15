from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from models.database import SessionLocal
from models.book import Book
import os

class CoverTile(QWidget):
    def __init__(self, book: Book, on_click):
        super().__init__()
        self.book = book
        self.on_click = on_click

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)

        # High-res cover thumbnail
        pix = QPixmap(book.thumbnail)
        lbl = QLabel()
        lbl.setPixmap(pix.scaled(
            180, 240,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        # Title right underneath
        title = QLabel(book.title or os.path.basename(book.path))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click(self.book)

class LibraryView(QScrollArea):
    def __init__(self, on_book_selected):
        super().__init__()
        self.on_book_selected = on_book_selected

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setHorizontalSpacing(20)
        self.grid.setVerticalSpacing(20)

        self.setWidget(container)
        self.setWidgetResizable(True)
        self.load_books()

    def load_books(self):
        session = SessionLocal()
        books = session.query(Book).order_by(Book.added_at.desc()).all()
        session.close()

        # Clear old tiles
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Populate (2 columns for larger covers)
        cols = 2
        for idx, book in enumerate(books):
            row, col = divmod(idx, cols)
            tile = CoverTile(book, self.on_book_selected)
            self.grid.addWidget(tile, row, col)
