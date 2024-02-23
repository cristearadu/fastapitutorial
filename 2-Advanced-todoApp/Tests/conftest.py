import pytest
import random
import requests
from faker import Faker

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def todo_url():
    return f"{BASE_URL}/todo"


@pytest.fixture(scope="session")
def auth_url():
    return f"{BASE_URL}/auth"


@pytest.fixture()
def basic_auth_token_body():
    return {"username": "radu_user", "password": "test1234"}


@pytest.fixture()
def auth_token_body_response(auth_url, basic_auth_token_body):
    response = requests.post(f"{auth_url}/token", data=basic_auth_token_body)
    response = response.json()
    return response


@pytest.fixture()
def auth_token(auth_token_body_response):
    return auth_token_body_response["access_token"]


@pytest.fixture()
def authenticated_session(auth_token):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return session


@pytest.fixture()
def random_auth_user_body_data():
    faker = Faker()
    first_name = faker.name()
    return {
        "username": f"{first_name}",
        "email": f"{first_name}@gmail.com",
        "first_name": f"{first_name}",
        "last_name": f"{faker.name()}",
        "role": "casual_user",
        "password": "test1234"
    }


@pytest.fixture()
def todo_example_body_data():
    """Generate test book data"""
    return {
        "title": f"Random Title",
        "description": "Random description",
        "priority": random.randint(1, 5),
        "complete": False,
    }


@pytest.fixture()
def random_todo_id(base_url, authenticated_session):
    """Generate example to do data"""
    response = authenticated_session.get(f"{base_url}/")
    books = response.json()
    if books:
        return random.choice(books)["id"]
    else:
        pytest.skip("No todo item was available to select")


@pytest.fixture()
def generated_todo_item(
    base_url, todo_url, authenticated_session, todo_example_body_data
):
    """Create a to do and return its ID, and ensure cleanup after test"""
    create_response = authenticated_session.post(
        f"{todo_url}", json=todo_example_body_data
    )
    assert create_response.status_code == 201, "Todo item has not been created"

    # Get last to do id
    get_response = authenticated_session.get(f"{base_url}/")
    assert get_response.status_code == 200
    todo_item = get_response.json()[-1]

    yield todo_item

    todo_id = todo_item["id"]
    delete_response = authenticated_session.delete(f"{todo_url}/{todo_id}")
    assert delete_response.status_code == 204, "Todo item could not be deleted"
