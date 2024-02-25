import pytest


class TestTodosCreate:
    @pytest.mark.dependency()
    def test_create_todo(self, todo_example_body_data, generated_todo_item):
        for todo_attribute, todo_value in todo_example_body_data.items():
            assert todo_example_body_data[todo_attribute] == todo_value

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
    def test_create_todo_invalid_parameters(
        self,
        todo_url,
        authenticated_session,
        todo_example_body_data,
        field,
        value,
        error_message,
    ):
        todo_body_data = {**todo_example_body_data, field: value}
        response = authenticated_session.post(f"{todo_url}", json=todo_body_data)
        assert response.status_code == 422
        assert error_message in response.text
