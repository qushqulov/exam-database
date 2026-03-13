from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal
from .models import Author, Book, Student, Borrow


# 2AUTHOR CRUD 


def create_author(name: str, bio: str = None) -> Author | None:
    """Yangi muallif yaratish"""
    try:
        with SessionLocal() as session:
            author = Author(name=name, bio=bio)
            session.add(author)
            session.commit()
            session.refresh(author)
            return author
    except IntegrityError:
        return None

def get_author_by_id(author_id: int) -> Author | None:
    """ID bo'yicha muallifni olish"""
    with SessionLocal() as session:
        return session.get(Author, author_id)

def get_all_authors() -> list[Author]:
    """Barcha mualliflar ro'yxatini olish"""
    with SessionLocal() as session:
        return list(session.scalars(select(Author)).all())

def update_author(author_id: int, name: str = None, bio: str = None) -> Author | None:
    """Muallif ma'lumotlarini yangilash"""
    with SessionLocal() as session:
        author = session.get(Author, author_id)
        if not author:
            return None
        if name:
            author.name = name
        if bio:
            author.bio = bio
        session.commit()
        session.refresh(author)
        return author

def delete_author(author_id: int) -> bool:
    """Muallifni o'chirish (faqat kitoblari bo'lmagan holda)"""
    with SessionLocal() as session:
        author = session.get(Author, author_id)
        # Shart: Muallif mavjud bo'lsa va uning kitoblari bo'lmasa o'chirish
        if not author or len(author.books) > 0:
            return False
        session.delete(author)
        session.commit()
        return True



#  BOOK CRUD


def create_book(title: str, author_id: int, published_year: int, isbn: str = None) -> Book | None:
    """Yangi kitob yaratish"""
    try:
        with SessionLocal() as session:
            book = Book(title=title, author_id=author_id, published_year=published_year, isbn=isbn)
            session.add(book)
            session.commit()
            session.refresh(book)
            return book
    except IntegrityError:
        return None

def get_book_by_id(book_id: int) -> Book | None:
    """ID bo'yicha kitobni olish"""
    with SessionLocal() as session:
        return session.get(Book, book_id)

def get_all_books() -> list[Book]:
    """Barcha kitoblar ro'yxatini olish"""
    with SessionLocal() as session:
        return list(session.scalars(select(Book)).all())

def search_books_by_title(title: str) -> list[Book]:
    """Kitoblarni sarlavha bo'yicha qidirish (partial match)"""
    with SessionLocal() as session:
        query = select(Book).where(Book.title.ilike(f"%{title}%"))
        return list(session.scalars(query).all())

def delete_book(book_id: int) -> bool:
    """Kitobni o'chirish"""
    with SessionLocal() as session:
        book = session.get(Book, book_id)
        if not book:
            return False
        session.delete(book)
        session.commit()
        return True



# STUDENT CRUD 

def create_student(full_name: str, email: str, grade: str = None) -> Student | None:
    """Yangi talaba ro'yxatdan o'tkazish"""
    try:
        with SessionLocal() as session:
            student = Student(full_name=full_name, email=email, grade=grade)
            session.add(student)
            session.commit()
            session.refresh(student)
            return student
    except IntegrityError:
        return None

def get_student_by_id(student_id: int) -> Student | None:
    """ID bo'yicha talabani olish"""
    with SessionLocal() as session:
        return session.get(Student, student_id)

def get_all_students() -> list[Student]:
    """Barcha talabalar ro'yxatini olish"""
    with SessionLocal() as session:
        return list(session.scalars(select(Student)).all())

def update_student_grade(student_id: int, grade: str) -> Student | None:
    """Talaba sinfini yangilash"""
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        student.grade = grade
        session.commit()
        session.refresh(student)
        return student



#  BORROW / RETURN


def borrow_book(student_id: int, book_id: int) -> Borrow | None:
    """Talabaga kitob berish mantiqi"""
    with SessionLocal() as session:
        # 1. Student va Book mavjudligini tekshirish
        student = session.get(Student, student_id)
        book = session.get(Book, book_id)
        if not student or not book:
            return None
        
        # 2. Kitobning is_available=True ekanligini tekshirish
        if not book.is_available:
            return None
            
        # 3. Talabada 3 tadan ortiq qaytarilmagan kitob yo'qligini tekshirish
        active_borrows_count = session.scalar(
            select(func.count(Borrow.id)).where(
                and_(Borrow.student_id == student_id, Borrow.returned_at == None)
            )
        )
        if active_borrows_count >= 3:
            return None

        # Transaction boshlandi
        try:
            borrow = Borrow(student_id=student_id, book_id=book_id)
            book.is_available = False
            session.add(borrow)
            session.commit()
            session.refresh(borrow)
            return borrow
        except Exception:
            session.rollback()
            return None

def return_book(borrow_id: int) -> bool:
    """Kitobni qaytarish mantiqi"""
    with SessionLocal() as session:
        borrow = session.get(Borrow, borrow_id)
        if not borrow or borrow.returned_at:
            return False
        
        try:
            borrow.returned_at = datetime.utcnow()
            # Borrow orqali bog'langan kitobning holatini o'zgartirish
            borrow.book.is_available = True
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False




def get_student_borrow_count(student_id: int) -> int:
    """Talabaning jami olgan kitoblari soni"""
    with SessionLocal() as session:
        return session.scalar(
            select(func.count(Borrow.id)).where(Borrow.student_id == student_id)
        ) or 0

def get_currently_borrowed_books() -> list[tuple]:
    """Hozirda band bo'lgan kitoblar, talabalar va olingan vaqt"""
    with SessionLocal() as session:
        query = select(Borrow).where(Borrow.returned_at == None)
        borrows = session.scalars(query).all()
        return [(b.book, b.student, b.borrowed_at) for b in borrows]

def get_books_by_author(author_id: int) -> list[Book]:
    """Muayyan muallifning barcha kitoblari"""
    with SessionLocal() as session:
        query = select(Book).where(Book.author_id == author_id)
        return list(session.scalars(query).all())

def get_overdue_borrows() -> list[tuple]:
    """Kechikkan kitoblar ro'yxati (Borrow, Student, Book, kechikkan_kunlar)"""
    with SessionLocal() as session:
        now = datetime.utcnow()
        query = select(Borrow).where(
            and_(Borrow.returned_at == None, Borrow.due_date < now)
        )
        borrows = session.scalars(query).all()
        
        result = []
        for b in borrows:
            overdue_days = (now - b.due_date).days
            result.append((b, b.student, b.book, overdue_days))
        return result