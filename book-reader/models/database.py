# models/database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Path to your SQLite file
DB_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "library.db")

# Use future=True so that .execute(text(...)) works as expected
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, future=True)
Base = declarative_base()

def init_db():
    # Create the normal tables
    Base.metadata.create_all(bind=ENGINE)
    # Create the FTS5 virtual table in a transaction
    with ENGINE.begin() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS book_fts
            USING fts5(content, book_id UNINDEXED);
        """))
