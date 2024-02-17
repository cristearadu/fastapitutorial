from typing import Optional
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, le=datetime.now().year)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'raduC',
                'description': 'A new description of a book',
                'rating': 5,
                'published_date': 2029
            }
        }


BOOKS = [
    Book(1, "Computer Science Pro", "Radu", "A very nice book", 5, 2010),
    Book(2, "Be Fast with FastAPI", "Radu", "A great book", 5, 2011),
    Book(3, "Master Endpoints", "Radu", "A awesome book", 5, 2012),
    Book(4, "HP1", "Author 1", "Book description", 2, 2013),
    Book(5, "HP2", "Author 2", "Book description", 3, 2014),
    Book(6, "HP3", "Author 3", "Book description", 4, 2015)
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/")
async def read_all_books(book_rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book


@app.post("/create/book")
async def create_book(book_request: BookRequest):
    # validations
    new_book = Book(**book_request.dict())
    BOOKS.append(find_book_id(new_book))


@app.put("/books/update_book")
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
