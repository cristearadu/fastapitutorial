import random
import pytest


class TestTodosUpdate:
    @pytest.mark.parametrize(
        "update_data",
        [
            {"title": "Updated title"},
            {"description": "Updated Description"},
            {"complete": True},
            {"complete": False},
            {"priority": random.randint(1, 5)},
        ],
    )
    def test_update_todo(
        self,
        todo_url,
        authenticated_session,
        todo_example_body_data,
        generated_todo_item,
        update_data,
    ):
        todo_example_body_data.update(update_data)
        response = authenticated_session.put(
            f"{todo_url}/{generated_todo_item['id']}", json=todo_example_body_data
        )
        assert response.status_code == 204, "Failed to update todo"

    @pytest.mark.parametrize(
        "field, value, error_message",
        [
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
        ],
    )
    def test_update_todo_negative(
        self,
        todo_url,
        authenticated_session,
        todo_example_body_data,
        generated_todo_item,
        field,
        value,
        error_message,
    ):
        todo_body_data = {**todo_example_body_data, field: value}
        response = authenticated_session.put(
            f"{todo_url}/{generated_todo_item['id']}", json=todo_body_data
        )
        assert response.status_code == 422
        assert error_message in response.text
