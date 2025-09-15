# models/book.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    title = Column(String, default="")
    author = Column(String, default="")
    thumbnail = Column(String, default="")
    last_pos = Column(Integer, default=0)  # last-read page or char
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
