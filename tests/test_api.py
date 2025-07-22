import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import Book

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def get_test_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Override DB dependency
app.dependency_overrides[get_db] = get_test_db

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Book Catalog API"}

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_get_empty_books(client: AsyncClient):
    response = await client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_book(client: AsyncClient):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "published_year": 2023,
        "summary": "A test book"
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_book_without_summary(client: AsyncClient):
    book_data = {
        "title": "Test Book No Summary",
        "author": "Test Author",
        "published_year": 2023
    }
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 201
    assert response.json()["summary"] is None

@pytest.mark.asyncio
async def test_create_book_empty_title(client: AsyncClient):
    response = await client.post("/books/", json={
        "title": "",
        "author": "Author",
        "published_year": 2023
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_book_future_year(client: AsyncClient):
    response = await client.post("/books/", json={
        "title": "Future Book",
        "author": "Author",
        "published_year": 3000
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_book_too_old_year(client: AsyncClient):
    response = await client.post("/books/", json={
        "title": "Ancient Book",
        "author": "Author",
        "published_year": 500
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_book(client: AsyncClient):
    res = await client.post("/books/", json={
        "title": "Get Me",
        "author": "Author",
        "published_year": 2020
    })
    book_id = res.json()["id"]
    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Me"

@pytest.mark.asyncio
async def test_get_nonexistent_book(client: AsyncClient):
    response = await client.get("/books/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_multiple_books(client: AsyncClient):
    for i in range(3):
        await client.post("/books/", json={
            "title": f"Book {i}",
            "author": "Author",
            "published_year": 2020 + i
        })
    res = await client.get("/books/")
    assert len(res.json()) == 3

@pytest.mark.asyncio
async def test_update_book(client: AsyncClient):
    res = await client.post("/books/", json={
        "title": "Old",
        "author": "Author",
        "published_year": 2019
    })
    book_id = res.json()["id"]
    response = await client.put(f"/books/{book_id}", json={
        "title": "New",
        "published_year": 2020
    })
    data = response.json()
    assert data["title"] == "New"
    assert data["published_year"] == 2020

@pytest.mark.asyncio
async def test_update_book_with_empty_payload(client: AsyncClient):
    res = await client.post("/books/", json={
        "title": "Unchanged",
        "author": "Author",
        "published_year": 2020
    })
    book_id = res.json()["id"]
    response = await client.put(f"/books/{book_id}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == "Unchanged"

@pytest.mark.asyncio
async def test_update_nonexistent_book(client: AsyncClient):
    res = await client.put("/books/999", json={"title": "X"})
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_update_book_validation_error(client: AsyncClient):
    res = await client.post("/books/", json={
        "title": "Bad",
        "author": "Author",
        "published_year": 2010
    })
    book_id = res.json()["id"]
    res = await client.put(f"/books/{book_id}", json={"published_year": 4000})
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_delete_book(client: AsyncClient):
    res = await client.post("/books/", json={
        "title": "Del",
        "author": "Author",
        "published_year": 2021
    })
    book_id = res.json()["id"]
    del_res = await client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204
    get_res = await client.get(f"/books/{book_id}")
    assert get_res.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_book(client: AsyncClient):
    res = await client.delete("/books/999")
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_books_pagination(client: AsyncClient):
    for i in range(5):
        await client.post("/books/", json={
            "title": f"Book {i}",
            "author": f"Author {i}",
            "published_year": 2020 + i
        })
    res = await client.get("/books/?skip=2&limit=2")
    data = res.json()
    assert res.status_code == 200
    assert len(data) == 2

@pytest.mark.asyncio
async def test_partial_deletion_then_fetch(client: AsyncClient):
    for i in range(3):
        await client.post("/books/", json={
            "title": f"B{i}",
            "author": "A",
            "published_year": 2022
        })
    res = await client.get("/books/")
    book_id = res.json()[0]["id"]
    await client.delete(f"/books/{book_id}")
    res2 = await client.get("/books/")
    assert len(res2.json()) == 2
