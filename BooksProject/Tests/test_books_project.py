import random

import pytest
import requests
from datetime import datetime


class TestBookPositive:
    def test_read_all_books(self, base_url):
        response = requests.get(f"{base_url}/books")
        assert response.status_code == 200
        assert isinstance(response.json(), list), "Response is not a list"

    def test_read_book_by_id(self, base_url, random_book_id):
        response = requests.get(f"{base_url}/books/{random_book_id}")
        assert response.status_code == 200
        book = response.json()
        assert book['id'] == random_book_id, "Book ID does not match"

    def test_create_book_positive(self, base_url, test_book_data):
        response = requests.post(f"{base_url}/create/book", json=test_book_data)
        assert response.status_code in [200, 201], "Failed to create book"

    @pytest.mark.parametrize("update_data", [
        {"title": "Updated Title A"},
        {"rating": 3},
        {"author": "Author_222"},
        {"Description": "NEW DESCRIPTION"},
        {"published_date": random.randint(2000, datetime.now().year)}
    ])
    def test_update_book_positive(self, base_url, test_book_data, random_book_id, update_data):

        test_book_data.update(update_data)
        response = requests.put(f"{base_url}/books/update_book", json={**test_book_data, "id": random_book_id})
        assert response.status_code == 200, "Failed to update book"

    def test_delete_book_positive(self, base_url, test_book_data):
        create_response = requests.post(f"{base_url}/create/book", json=test_book_data)
        assert create_response.status_code in [200, 201], "Failed to create book for deletion test"
        response = requests.get(f"{base_url}/books")
        book_id = response.json()[-1]['id']
        delete_response = requests.delete(f"{base_url}/books/{book_id}")
        assert delete_response.status_code == 200, "Failed to delete book"


class TestBookCreationNegative:
    @pytest.mark.parametrize("field, value, error_message", [
        ("title", "", "String should have at least 3 characters"),
        ("title", 1, "Input should be a valid string"),
        ("author", "", "String should have at least 1 character"),
        ("author", 1, "Input should be a valid string"),
        ("rating", 0, "Input should be greater than 0"),
        ("rating", 6, "Input should be less than 6"),
        ("rating", "a", "Input should be a valid integer"),
        ("rating", 1.1, "Input should be a valid integer, got a number with a fractional part"),
        ("published_date", 1999, "Input should be greater than 1999"),
        ("published_date", 1999.1, "Input should be a valid integer, got a number with a fractional part"),
        ("published_date", "a", "Input should be a valid integer"),
        ("published_date", datetime.now().year + 1, "Input should be less than or equal to 2024")
    ])
    def test_create_book_negative(self, base_url, field, value, error_message):
        book_data = {
            "title": "Valid Title",
            "author": "Valid Author",
            "rating": 5,
            "published_date": 2021,
            field: value}
        response = requests.post(f"{base_url}/create/book", json=book_data)
        assert response.status_code == 422
        assert error_message in response.text


class TestBookUpdateNegative:
    @pytest.mark.parametrize("field, value, error_message", [
        ("title", "", "String should have at least 3 characters"),
        ("title", 1, "Input should be a valid string"),
        ("author", "", "String should have at least 1 character"),
        ("author", 1, "Input should be a valid string"),
        ("rating", 0, "Input should be greater than 0"),
        ("rating", 6, "Input should be less than 6"),
        ("rating", "a", "Input should be a valid integer"),
        ("rating", 1.1, "Input should be a valid integer, got a number with a fractional part"),
        ("published_date", 1999, "Input should be greater than 1999"),
        ("published_date", 1999.1, "Input should be a valid integer, got a number with a fractional part"),
        ("published_date", "a", "Input should be a valid integer"),
        ("published_date", datetime.now().year + 1, "Input should be less than or equal to 2024")
    ])
    def test_update_book_negative(self, base_url, test_book_data, random_book_id, field, value, error_message):
        test_book_data.update({
            "id": random_book_id,
            field: value
        })
        response = requests.put(f"{base_url}/books/update_book", json=test_book_data)
        assert response.status_code == 422
        assert error_message in response.text


class TestBookDeletionNegative:
    @pytest.mark.parametrize("book_id, expected_status_code", [
        (0, 422),
        ("a", 422),
        (1.5, 422)
    ])
    def test_delete_book_negative(self, base_url, book_id, expected_status_code):
        response = requests.get(f"{base_url}/books/{book_id}")
        assert response.status_code == expected_status_code


class TestReadBookByIdNegative:
    @pytest.mark.parametrize("book_id, expected_status_code", [
        (0, 422),
        ("a", 422),
        (1.5, 422)
    ])
    def test_read_book_by_id_negative(self, base_url, book_id, expected_status_code):
        response = requests.get(f"{base_url}/books/{book_id}")
        assert response.status_code == expected_status_code

