import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text


from models.database import init_db, SessionLocal
from models.book import Book

from services.pdf import (
    extract_pdf_cover, extract_pdf_text, extract_pdf_metadata
)
from services.epub import (
    extract_epub_cover, extract_epub_text, extract_epub_metadata
)

# helper to wait until the file is fully writable
def wait_for_file(path, timeout=10, interval=0.5):
    start = time.time()
    while True:
        try:
            # try opening for read + write
            with open(path, "rb"):
                return True
        except PermissionError:
            if time.time() - start > timeout:
                return False
            time.sleep(interval)

# initialize DB
init_db()
session = SessionLocal()

class LibraryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        src = event.src_path
        print(f"Detected new file: {src}")
        # wait until file is readable (not locked)
        if not wait_for_file(src):
            print(f"❌ Timeout waiting for file to be ready: {src}")
            return

        name, ext = os.path.splitext(src.lower())
        thumb_dir = os.path.join(os.path.dirname(__file__), os.pardir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        try:
            if ext == ".pdf":
                cover = extract_pdf_cover(src)
                meta  = extract_pdf_metadata(src)
                full_text = extract_pdf_text(src)
            elif ext == ".epub":
                cover = extract_epub_cover(src)
                meta  = extract_epub_metadata(src)
                full_text = extract_epub_text(src)
            else:
                print(f"Ignoring unsupported file type: {src}")
                return
        except Exception as e:
            print(f"❌ Error extracting data from {src}: {e}")
            return

        # Save thumbnail
        base = os.path.basename(name)
        thumb_path = os.path.join(thumb_dir, f"{base}.png")
        with open(thumb_path, "wb") as f:
            f.write(cover)
        print(f"✅ Thumbnail saved: {thumb_path}")

        # Persist to DB
        book = Book(
            path=src,
            title=meta.get("title", ""),
            author=meta.get("author", ""),
            thumbnail=thumb_path,
        )
        try:
            session.add(book)
            session.commit()
            # Index full-text
            session.execute(
                text("INSERT INTO book_fts(rowid, content, book_id) VALUES (:rid, :cnt, :bid)"),
                {"rid": book.id, "cnt": full_text, "bid": book.id}
            )

            session.commit()
            print(f"📚 Book added: {book.title} by {book.author}")
        except IntegrityError:
            session.rollback()
            print("🔄 Book already in library, skipping.")

if __name__ == "__main__":
    library_path = os.path.join(os.path.dirname(__file__), os.pardir, "Library")
    os.makedirs(library_path, exist_ok=True)
    print("→ Watching folder:", os.path.abspath(library_path))

    handler = LibraryHandler()
    observer = Observer()
    observer.schedule(handler, library_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
