import pytest
import random
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def test_book_data():
    """Generate test book data"""
    return {
        "title": "Example Title",
        "author": "Example Author",
        "description": "Random description",
        "rating": random.randint(1, 5),
        "published_date": random.randint(2000, datetime.now().year)
    }


@pytest.fixture(scope="function")
def random_book_id(base_url):
    """Fixture to fetch a random book ID"""
    response = requests.get(f"{base_url}/books")
    books = response.json()
    if books:
        return random.choice(books)['id']
    else:
        pytest.skip("No books available to select a random ID")
