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


@pytest.fixture(scope="session")
def user_url():
    return f"{BASE_URL}/user/"


@pytest.fixture(scope="session")
def user_creation_and_deletion(auth_url, user_url, random_auth_user_body_data):
    create_response = requests.post(f"{auth_url}", json=random_auth_user_body_data)
    assert create_response.status_code == 201, "User was not successfully created"

    token_response = requests.post(f"{auth_url}/token", data=random_auth_user_body_data)
    assert token_response.status_code == 200, "Authentication failed for the created user"
    token = token_response.json()["access_token"]

    yield {"username": random_auth_user_body_data["username"],
           "password": random_auth_user_body_data["password"],
           "email": random_auth_user_body_data["email"]}

    headers = {"Authorization": f"Bearer {token}"}
    delete_response = requests.delete(user_url, headers=headers,
                                      json={"password": random_auth_user_body_data["password"]})
    assert delete_response.status_code == 204, "User could not be deleted after the test"
    delete_response = requests.delete(user_url, headers=headers,
                                      json={"password": random_auth_user_body_data["password"]})
    assert delete_response.status_code == 401, "User could not be deleted after the test"


@pytest.fixture()
def auth_token_body_response(auth_url, user_creation_and_deletion):
    request_auth_data = user_creation_and_deletion.copy()
    request_auth_data.pop("email")
    response = requests.post(f"{auth_url}/token", data=request_auth_data)
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


@pytest.fixture(scope="session")
def random_auth_user_body_data():
    faker = Faker()
    first_name = faker.name()
    return {
        "username": f"{first_name}",
        "email": f"{first_name}@gmail.com".replace(" ", ""),
        "first_name": f"{first_name}",
        "last_name": f"{faker.name()}",
        "role": random.choice(["casual_user", "admin"]),
        "password": "test1234",
        "phone_number": "0777777777"
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
def generated_todo_item(base_url, todo_url, authenticated_session, todo_example_body_data):
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
