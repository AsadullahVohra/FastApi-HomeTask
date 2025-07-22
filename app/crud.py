from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .models import Book
from .schemas import BookCreate, BookUpdate

async def get_book(db: AsyncSession, book_id: int) -> Optional[Book]:
    """Retrieve a single book by ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()

async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
    """Retrieve all books with pagination."""
    result = await db.execute(select(Book).offset(skip).limit(limit))
    return result.scalars().all()

async def create_book(db: AsyncSession, book: BookCreate) -> Book:
    """Create a new book."""
    db_book = Book(**book.dict())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def update_book(db: AsyncSession, book_id: int, book_update: BookUpdate) -> Optional[Book]:
    """Update an existing book."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    
    if not db_book:
        return None
    
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def delete_book(db: AsyncSession, book_id: int) -> bool:
    """Delete a book by ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    
    if not db_book:
        return False
    
    await db.delete(db_book)
    await db.commit()
    return True