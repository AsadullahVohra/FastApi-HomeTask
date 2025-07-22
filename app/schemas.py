from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: str = Field(..., min_length=1, max_length=100, description="Book author")
    published_year: int = Field(..., ge=1000, le=datetime.now().year, description="Publication year")
    summary: Optional[str] = Field(None, max_length=1000, description="Book summary")

    @validator('title', 'author')
    def validate_strings(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

    @validator('published_year')
    def validate_published_year(cls, v):
        current_year = datetime.now().year
        if v < 1000 or v > current_year:
            raise ValueError(f'Published year must be between 1000 and {current_year}')
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    published_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    summary: Optional[str] = Field(None, max_length=1000)

    @validator('title', 'author', pre=True)
    def validate_strings(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v else v

    @validator('published_year')
    def validate_published_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1000 or v > current_year:
                raise ValueError(f'Published year must be between 1000 and {current_year}')
        return v

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True