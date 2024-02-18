import pytest
import random
import requests


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def todo_url():
    return f"{BASE_URL}/todo"


@pytest.fixture(scope="function")
def example_body_data():
    """Generate test book data"""
    return {
        "title": "Example Title",
        "description": "Random description",
        "priority": random.randint(1, 5),
        "complete": False,
    }


@pytest.fixture(scope="function")
def random_todo_id(base_url):
    """Generate example to do data"""
    response = requests.get(f"{base_url}/")
    books = response.json()
    if books:
        return random.choice(books)['id']
    else:
        pytest.skip("No todo item was available to select")


@pytest.fixture(scope="function")
def generated_todo_item(base_url, todo_url, example_body_data):
    """Create a to do and return its ID, and ensure cleanup after test"""
    create_response = requests.post(f"{todo_url}", json=example_body_data)
    assert create_response.status_code == 201, "Todo item has not been created"

    # Get last to do id
    get_response = requests.get(f"{base_url}/")
    assert get_response.status_code == 200
    todo_item = get_response.json()[-1]

    yield todo_item

    todo_id = todo_item['id']
    delete_response = requests.delete(f"{todo_url}/{todo_id}")
    assert delete_response.status_code == 204, "Todo item could not be deleted"
