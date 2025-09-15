from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt, QSize
from services.pdf import extract_pdf_page_image, extract_pdf_page_text
from services.tts import TTSPlayer
from models.database import SessionLocal
from models.book import Book
import fitz
import numpy as np
import sounddevice as sd

class ReaderView(QWidget):
    def __init__(self, book: Book, on_back):
        super().__init__()
        self.book = book
        self.on_back = on_back

        # Initialize Kokoro TTS player: faster speed, sentence-level split
        sentence_pattern = r'(?<=[\.\?\!])\s+'
        self.tts = TTSPlayer(voice='af_heart', speed=1.3, split_pattern=sentence_pattern)
        self.is_playing = False

        # Open PDF via PyMuPDF for page count
        self.doc = fitz.open(self.book.path)
        self.page_count = self.doc.page_count
        self.current_page = book.last_pos or 0

        self.init_ui()
        self.show_page(self.current_page)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Navigation bar
        nav = QHBoxLayout()
        back_btn = QPushButton("← Back to Library")
        back_btn.clicked.connect(self.on_back)
        nav.addWidget(back_btn)

        prev_btn = QPushButton("◀ Previous")
        prev_btn.clicked.connect(self.prev_page)
        nav.addWidget(prev_btn)

        next_btn = QPushButton("Next ▶")
        next_btn.clicked.connect(self.next_page)
        nav.addWidget(next_btn)

        # Play/Pause button
        self.play_btn = QPushButton("► Listen")
        self.play_btn.clicked.connect(self.toggle_play)
        nav.addWidget(self.play_btn)

        layout.addLayout(nav)

        # Scrollable PDF image view
        self.scroll = QScrollArea()
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.page_label)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.setLayout(layout)

    def show_page(self, num: int):
        # Stop any speech if playing
        if self.is_playing:
            self.tts.stop()
            self.play_btn.setText("► Listen")
            self.is_playing = False

        # Render and display page image
        pix = extract_pdf_page_image(
            self.book.path,
            num,
            QSize(800, 1200)
        )
        if pix:
            self.page_label.setPixmap(pix)

        # Persist last-read page
        session = SessionLocal()
        session.query(Book).filter(Book.id == self.book.id).update({"last_pos": num})
        session.commit()
        session.close()

    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def toggle_play(self):
        if not self.is_playing:
            # Pull in *just* the current page’s text
            page_text = extract_pdf_page_text(
                self.book.path,
                self.current_page
            ).strip()

            if not page_text:
                # nothing to read on this page
                return

            # Speak it all in one shot
            self.tts.speak(page_text)
            self.play_btn.setText("❚❚ Pause")
        else:
            # Stop playback
            self.tts.stop()
            self.play_btn.setText("► Listen")
        self.is_playing = not self.is_playing


    def closeEvent(self, event):
        # Cleanup on close
        self.doc.close()
        if self.is_playing:
            self.tts.stop()
            sd.stop()
        super().closeEvent(event)
