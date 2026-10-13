from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Author(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=False, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, unique=False, nullable=False)
    date_of_death: Mapped[date | None] = mapped_column(Date, unique=False, nullable=True)
    books: Mapped[list[Book]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Author {self.id}: {self.name!r}>"

    def __str__(self):
        return f"Author: ID: {self.id}, Name: {self.name}, Birthdate: {self.birth_date}, Deathdate: {self.date_of_death}"


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(80), unique=False, nullable=False)
    publication_year: Mapped[date] = mapped_column(Date, unique=False, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('author.id'), nullable=False)
    author: Mapped["Author"]=relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.id}: {self.isbn!r}>"

    def __str__(self):
        return f"Author: ID: {self.id}, ISBN: {self.isbn}, Title: {self.title}, Publication year: {self.publication_year}, author_id: {self.author_id}"
