import random

import pytest
import requests


class TestTodoEndpointsPositive:
    def test_read_all_todos(self, base_url):
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert isinstance(response.json(), list), "Response is not a list"

    def test_read_todo_by_id(self, todo_url, generated_todo_item):
        response = requests.get(f"{todo_url}/{generated_todo_item['id']}")
        assert response.status_code == 200
        todo_item = response.json()
        assert todo_item['id'] == generated_todo_item['id'], "todo ID does not match"

    @pytest.mark.dependency()
    def test_create_todo(self, example_body_data, generated_todo_item):
        for todo_attribute, todo_value in example_body_data.items():
            assert example_body_data[todo_attribute] == todo_value

    @pytest.mark.parametrize("update_data", [
        {"title": "Updated title"},
        {"description": "Updated Description"},
        {"complete": True},
        {"complete": False},
        {"priority": random.randint(1, 5)}
    ])
    def test_update_todo(self, todo_url, example_body_data, generated_todo_item, update_data):

        example_body_data.update(update_data)
        response = requests.put(f"{todo_url}/{generated_todo_item['id']}", json=example_body_data)
        assert response.status_code == 204, "Failed to update todo"

    @pytest.mark.dependency(depeonds=["test_create_todo"])
    def test_delete_todo(self, generated_todo_item):
        pass


class TestCreateTodoNegative:
    @pytest.mark.parametrize("field, value, error_message", [
        ("title", "ab", "String should have at least 3 characters"),
        ("title", "", "String should have at least 3 characters"),
        ("title", 1, "Input should be a valid string"),
        ("title", 1.1, "Input should be a valid string"),
        ("title", None, "Input should be a valid string"),
        ("title", True, "Input should be a valid string"),
        ("description", "ab", "String should have at least 3 characters"),
        ("description", "", "String should have at least 3 characters"),
        ("description", 1, "Input should be a valid string"),
        ("description", 1.1, "Input should be a valid string"),
        ("description", None, "Input should be a valid string"),
        ("description", True, "Input should be a valid string"),
        ("priority", "random string", "Input should be a valid integer"),
        ("priority", 1.1, "Input should be a valid integer"),
        ("priority", None, "Input should be a valid integer"),
        ("priority", False, "Input should be greater than 0"),
        ("priority", 0, "Input should be greater than 0"),
        ("priority", 6, "Input should be less than 6"),

    ])
    def test_create_todo_negative(self, todo_url, example_body_data, field, value, error_message):
        todo_body_data = {
            **example_body_data,
            field: value
        }
        response = requests.post(f"{todo_url}", json=todo_body_data)
        assert response.status_code == 422
        assert error_message in response.text


class TestUpdateTodoNegative:
    @pytest.mark.parametrize("field, value, error_message", [
        ("title", "ab", "String should have at least 3 characters"),
        ("title", "", "String should have at least 3 characters"),
        ("title", 1, "Input should be a valid string"),
        ("title", 1.1, "Input should be a valid string"),
        ("title", None, "Input should be a valid string"),
        ("title", True, "Input should be a valid string"),
        ("description", "ab", "String should have at least 3 characters"),
        ("description", "", "String should have at least 3 characters"),
        ("description", 1, "Input should be a valid string"),
        ("description", 1.1, "Input should be a valid string"),
        ("description", None, "Input should be a valid string"),
        ("description", True, "Input should be a valid string"),
        ("priority", "random string", "Input should be a valid integer"),
        ("priority", 1.1, "Input should be a valid integer"),
        ("priority", None, "Input should be a valid integer"),
        ("priority", False, "Input should be greater than 0"),
        ("priority", 0, "Input should be greater than 0"),
        ("priority", 6, "Input should be less than 6"),
    ])
    def test_update_todo_negative(self, todo_url, example_body_data, random_todo_id, field, value, error_message):
        todo_body_data = {
            **example_body_data,
            field: value
        }
        response = requests.put(f"{todo_url}/{random_todo_id}", json=todo_body_data)
        assert response.status_code == 422
        assert error_message in response.text


class TestDeleteTodoNegative:
    @pytest.mark.parametrize("invalid_todo_id, expected_status_code, error_message", [
        (0, 422, "Input should be greater than 0"),
        ("a", 422, "Input should be a valid integer, unable to parse string as an integer"),
        (1.5, 422, "Input should be a valid integer")
    ])
    def test_delete_book_negative(self, todo_url, invalid_todo_id, expected_status_code, error_message):
        response = requests.delete(f"{todo_url}/{invalid_todo_id}")
        assert response.status_code == expected_status_code
        assert error_message in response.text


class TestTodoByidNegative:
    @pytest.mark.parametrize("invalid_todo_id, expected_status_code, error_message", [
        (0, 422, "Input should be greater than 0"),
        ("a", 422, "Input should be a valid integer, unable to parse string as an integer"),
        (None, 422, "Input should be a valid integer")
    ])
    def test_get_todo_by_id_negative(self, todo_url, invalid_todo_id, expected_status_code, error_message):
        response = requests.get(f"{todo_url}/{invalid_todo_id}")
        assert response.status_code == expected_status_code
        assert error_message in response.text
