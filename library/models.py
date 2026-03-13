from datetime import datetime, timedelta

from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Author(Base):
    """
    Muallif modeli.

    Ushbu model kutubxonadagi mualliflar haqidagi ma'lumotlarni saqlaydi.

    Maydonlar:
        id (int): Muallifning yagona identifikatori.
        name (str): Muallifning ismi.
        bio (str | None): Muallif haqida qisqacha ma'lumot.
        created_at (datetime): Muallif bazaga qo'shilgan vaqt.

    Bog'lanishlar:
        books (list[Book]): Ushbu muallif yozgan kitoblar ro'yxati.
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")


class Book(Base):
    """
    Kitob modeli.

    Kutubxonadagi kitoblar haqida ma'lumotlarni saqlaydi.

    Maydonlar:
        id (int): Kitob identifikatori.
        title (str): Kitob nomi.
        author_id (int): Muallif identifikatori (Foreign Key).
        published_year (int): Kitob nashr qilingan yil.
        isbn (str | None): Kitobning ISBN raqami.
        is_available (bool): Kitob mavjud yoki yo'qligini bildiradi.
        created_at (datetime): Kitob bazaga qo'shilgan vaqt.
        updated_at (datetime): Oxirgi yangilangan vaqt.

    Bog'lanishlar:
        author (Author): Kitobning muallifi.
        borrows (list[Borrow]): Ushbu kitob bo'yicha olingan yozuvlar.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("authors.id"), nullable=False
    )
    published_year: Mapped[int] = mapped_column(Integer)
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    borrows: Mapped[list["Borrow"]] = relationship("Borrow", back_populates="book")


class Student(Base):
    """
    Talaba modeli.

    Kutubxona tizimidan foydalanadigan talabalar haqida
    ma'lumotlarni saqlaydi.

    Maydonlar:
        id (int): Talabaning identifikatori.
        full_name (str): Talabaning to'liq ismi.
        email (str): Talabaning email manzili.
        grade (str | None): Talabaning kursi yoki sinfi.
        registered_at (datetime): Talaba ro'yxatdan o'tgan vaqt.

    Bog'lanishlar:
        borrows (list[Borrow]): Talabaning olgan kitoblari ro'yxati.
    """

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    borrows: Mapped[list["Borrow"]] = relationship("Borrow", back_populates="student")


class Borrow(Base):
    """
    Kitob olish (Borrow) modeli.

    Ushbu model talabaning kutubxonadan kitob olishi
    jarayonini ifodalaydi.

    Maydonlar:
        id (int): Borrow yozuvi identifikatori.
        student_id (int): Kitobni olgan talaba ID.
        book_id (int): Olingan kitob ID.
        borrowed_at (datetime): Kitob olingan vaqt.
        due_date (datetime): Kitobni qaytarish muddati (14 kun).
        returned_at (datetime | None): Kitob qaytarilgan vaqt.

    Bog'lanishlar:
        student (Student): Kitobni olgan talaba.
        book (Book): Olingan kitob.
    """

    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(days=14), nullable=False
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    student: Mapped["Student"] = relationship("Student", back_populates="borrows")
    book: Mapped["Book"] = relationship("Book", back_populates="borrows")
