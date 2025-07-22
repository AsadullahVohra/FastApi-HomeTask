import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base
from app.models import Book
from app.schemas import BookCreate, BookUpdate
from app import crud

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_book(db_session):
    """Test creating a new book."""
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        summary="A test book summary"
    )
    
    book = await crud.create_book(db_session, book_data)
    
    assert book.id is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.published_year == 2023
    assert book.summary == "A test book summary"

@pytest.mark.asyncio
async def test_get_book(db_session):
    """Test retrieving a book by ID."""
    # Create a book first
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023
    )
    created_book = await crud.create_book(db_session, book_data)
    
    # Retrieve the book
    retrieved_book = await crud.get_book(db_session, created_book.id)
    
    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "Test Book"

@pytest.mark.asyncio
async def test_get_nonexistent_book(db_session):
    """Test retrieving a non-existent book."""
    book = await crud.get_book(db_session, 999)
    assert book is None

@pytest.mark.asyncio
async def test_get_books(db_session):
    """Test retrieving all books."""
    # Create multiple books
    for i in range(3):
        book_data = BookCreate(
            title=f"Test Book {i}",
            author=f"Test Author {i}",
            published_year=2020 + i
        )
        await crud.create_book(db_session, book_data)
    
    books = await crud.get_books(db_session)
    assert len(books) == 3

@pytest.mark.asyncio
async def test_update_book(db_session):
    """Test updating an existing book."""
    # Create a book first
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        published_year=2020
    )
    created_book = await crud.create_book(db_session, book_data)
    
    # Update the book
    update_data = BookUpdate(
        title="Updated Title",
        published_year=2021
    )
    updated_book = await crud.update_book(db_session, created_book.id, update_data)
    
    assert updated_book is not None
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Original Author"  # Should remain unchanged
    assert updated_book.published_year == 2021

@pytest.mark.asyncio
async def test_update_nonexistent_book(db_session):
    """Test updating a non-existent book."""
    update_data = BookUpdate(title="Updated Title")
    updated_book = await crud.update_book(db_session, 999, update_data)
    assert updated_book is None

@pytest.mark.asyncio
async def test_delete_book(db_session):
    """Test deleting a book."""
    # Create a book first
    book_data = BookCreate(
        title="To Be Deleted",
        author="Test Author",
        published_year=2023
    )
    created_book = await crud.create_book(db_session, book_data)
    
    # Delete the book
    deleted = await crud.delete_book(db_session, created_book.id)
    assert deleted is True
    
    # Verify it's gone
    retrieved_book = await crud.get_book(db_session, created_book.id)
    assert retrieved_book is None

@pytest.mark.asyncio
async def test_delete_nonexistent_book(db_session):
    """Test deleting a non-existent book."""
    deleted = await crud.delete_book(db_session, 999)
    assert deleted is False