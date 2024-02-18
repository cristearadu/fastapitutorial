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
