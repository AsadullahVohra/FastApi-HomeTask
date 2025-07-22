from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .database import engine, get_db
from .models import Base
from .schemas import BookResponse, BookCreate, BookUpdate
from . import crud

app = FastAPI(
    title="Book Catalog API",
    description="A simple CRUD API for managing books",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", summary="Root endpoint")
async def root():
    """Welcome message for the API."""
    return {"message": "Welcome to the Book Catalog API"}

@app.get("/books/", response_model=List[BookResponse], summary="List all books")
async def list_books(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all books with optional pagination.
    
    - **skip**: Number of books to skip (for pagination)
    - **limit**: Maximum number of books to return
    """
    books = await crud.get_books(db=db, skip=skip, limit=limit)
    return books

@app.get("/books/{book_id}", response_model=BookResponse, summary="Get a book by ID")
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single book by its ID.
    
    - **book_id**: The ID of the book to retrieve
    """
    book = await crud.get_book(db=db, book_id=book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book

@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, summary="Create a new book")
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new book.
    
    - **title**: The book's title (required)
    - **author**: The book's author (required)
    - **published_year**: Year the book was published (required)
    - **summary**: Optional book summary
    """
    return await crud.create_book(db=db, book=book)

@app.put("/books/{book_id}", response_model=BookResponse, summary="Update a book")
async def update_book(
    book_id: int, 
    book_update: BookUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing book.
    
    - **book_id**: The ID of the book to update
    - **title**: New title (optional)
    - **author**: New author (optional)
    - **published_year**: New publication year (optional)
    - **summary**: New summary (optional)
    """
    updated_book = await crud.update_book(db=db, book_id=book_id, book_update=book_update)
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return updated_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a book")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a book by its ID.
    
    - **book_id**: The ID of the book to delete
    """
    deleted = await crud.delete_book(db=db, book_id=book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )

# Health check endpoint
@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}