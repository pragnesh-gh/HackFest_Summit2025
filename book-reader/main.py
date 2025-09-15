import sys, os
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QStackedWidget

from ui.library_view import LibraryView
from ui.reader_view import ReaderView

if __name__ == "__main__":
    # Make sure Qt can find its plugins (e.g. for WebEngine, if you add that later)
    plugin_path = os.path.join(os.path.dirname(QtCore.__file__), "plugins")
    QtCore.QCoreApplication.addLibraryPath(plugin_path)

    app = QApplication(sys.argv)
    stack = QStackedWidget()

    # Callback to switch to the reader
    def show_reader(book):
        reader = ReaderView(
            book,
            on_back=lambda: stack.setCurrentWidget(lib_view)
        )
        stack.addWidget(reader)
        stack.setCurrentWidget(reader)

    # The library view is the main entry
    lib_view = LibraryView(on_book_selected=show_reader)
    stack.addWidget(lib_view)

    stack.resize(1024, 768)
    stack.show()
    sys.exit(app.exec())
