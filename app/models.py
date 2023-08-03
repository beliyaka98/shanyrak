from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    phone = Column(String)
    hashed_password = Column(String)
    name = Column(String)
    city = Column(String)

    adverts = relationship("Advert", back_populates="owner")
    comments = relationship("Comment", back_populates="author")

class Advert(Base):
    __tablename__ = "adverts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    price = Column(Integer)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="adverts")
    comments = relationship("Comment", back_populates="advert")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime)
    advert_id = Column(Integer, ForeignKey("adverts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    advert = relationship("Advert", back_populates="comments")
    author = relationship("User", back_populates="comments")