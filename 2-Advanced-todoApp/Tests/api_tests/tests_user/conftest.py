import pytest
from faker import Faker


@pytest.fixture()
def generate_user_data():
    faker = Faker()
    first_name = faker.name()
    last_name = faker.name()
    return {
        "username": f"{first_name}{last_name}",
        "email": f"{first_name}{last_name}@gmail.com".replace(" ", ""),
        "first_name": f"{first_name}",
        "last_name": f"{last_name}",
        "role": "casual_user",
        "password": "test1234",
        "phone_number": "0777777777"
    }
