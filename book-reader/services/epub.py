# services/epub.py

from ebooklib import epub
from PIL import Image
from io import BytesIO

def extract_epub_cover(path, max_size=(300, 400)):
    """
    Pull the EPUB cover image (if defined) and resize it to a thumbnail.
    Returns bytes of PNG data, or None if no image found.
    """
    book = epub.read_epub(path)

    cover_item = None
    images = []

    # 1) Gather all image items
    for item in book.get_items():
        if hasattr(item, "media_type") and item.media_type.startswith("image/"):
            images.append(item)
            name = item.get_name().lower()
            item_id = getattr(item, "id", "").lower()
            if "cover" in name or "cover" in item_id:
                cover_item = item
                break

    # 2) Fallback: first image if no explicit cover found
    if not cover_item and images:
        cover_item = images[0]

    if not cover_item:
        return None

    # 3) Resize and convert to PNG bytes
    img = Image.open(BytesIO(cover_item.get_content()))
    img.thumbnail(max_size)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
# at the bottom of services/epub.py
def extract_epub_text(path):
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(path)
    text_chunks = []
    for item in book.get_items():
        if hasattr(item, "media_type") and item.media_type == "application/xhtml+xml":
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text_chunks.append(soup.get_text())
    return "\n".join(text_chunks)

def extract_epub_metadata(path):
    from ebooklib import epub

    book = epub.read_epub(path)
    title = book.get_metadata("DC", "title")
    author = book.get_metadata("DC", "creator")
    return {
        "title": title[0][0] if title else "",
        "author": author[0][0] if author else "",
    }
