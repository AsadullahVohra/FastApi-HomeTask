# FastApi-HomeTask
A RESTful API for managing a book catalog built with FastAPI, SQLAlchemy, and Pydantic.

## Features

- ✅ Full CRUD operations for books
- ✅ Asynchronous endpoints using async/await
- ✅ SQLAlchemy ORM with SQLite database
- ✅ Pydantic models for request/response validation
- ✅ Comprehensive error handling
- ✅ Unit and integration tests
- ✅ Auto-generated OpenAPI documentation
- ✅ Input validation and sanitization

## Book Model

Each book has the following fields:
- `id`: Integer, primary key (auto-generated)
- `title`: String, required (1-200 characters)
- `author`: String, required (1-100 characters)
- `published_year`: Integer, required (1000 - current year)
- `summary`: String, optional (max 1000 characters)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books/` | List all books (with pagination) |
| GET | `/books/{id}` | Get a specific book by ID |
| POST | `/books/` | Create a new book |
| PUT | `/books/{id}` | Update an existing book |
| DELETE | `/books/{id}` | Delete a book |
| GET | `/` | Welcome message |
| GET | `/health` | Health check |

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd book-catalog
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

### API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app tests/
```

### Run Specific Test Files

```bash
# Unit tests
pytest tests/test_crud.py

# Integration tests
pytest tests/test_api.py
```

## Usage Examples

### Create a Book

```bash
curl -X POST "http://localhost:8000/books/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Great Gatsby",
       "author": "F. Scott Fitzgerald",
       "published_year": 1925,
       "summary": "A classic American novel set in the Jazz Age."
     }'
```

### Get All Books

```bash
curl "http://localhost:8000/books/"
```

### Get a Specific Book

```bash
curl "http://localhost:8000/books/1"
```

### Update a Book

```bash
curl -X PUT "http://localhost:8000/books/1" \
     -H "Content-Type: application/json" \
     -d '{"title": "The Great Gatsby (Updated)"}'
```

### Delete a Book

```bash
curl -X DELETE "http://localhost:8000/books/1"
```

## Project Structure

```
book_catalog/
├── app/                    # Application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app and route definitions
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic models
│   ├── database.py        # Database configuration
│   └── crud.py            # Database operations
├── tests/                 # Test package
│   ├── __init__.py
│   ├── test_crud.py       # Unit tests for CRUD operations
│   └── test_api.py        # Integration tests for API endpoints
├── requirements.txt       # Project dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Key Features Implemented

### Async Support
- All database operations use async/await
- FastAPI endpoints are asynchronous where appropriate
- Uses aiosqlite for async SQLite operations

### Validation & Error Handling
- Comprehensive Pydantic validation
- Proper HTTP status codes
- Descriptive error messages
- Input sanitization (whitespace trimming)

### Testing Strategy
- Unit tests for business logic (CRUD operations)
- Integration tests for API endpoints
- Test database isolation using in-memory SQLite
- Comprehensive test coverage for happy path and error cases

### Code Quality
- Type hints throughout the codebase
- Proper separation of concerns
- Clear naming conventions
- Comprehensive documentation

## Environment Variables

- `DATABASE_URL`: Database connection string (default: sqlite+aiosqlite:///./books.db)

## Development Notes

- The application uses SQLite by default for simplicity
- Database tables are created automatically on startup
- The API follows REST conventions
- All responses include proper HTTP status codes
- Input validation prevents common security issues

## License

This project is created as a take-home assignment demonstration.