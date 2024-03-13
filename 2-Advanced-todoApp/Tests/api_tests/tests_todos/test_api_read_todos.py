import pytest


class TestTodosRead:
    def test_read_all_todos(self, todo_url, authenticated_session):
        response = authenticated_session.get(todo_url)
        assert response.status_code == 200
        assert isinstance(response.json(), list), "Response is not a list"

    def test_read_todo_by_id(
        self, todo_url, authenticated_session, generated_todo_item
    ):
        response = authenticated_session.get(f"{todo_url}/{generated_todo_item['id']}")
        assert response.status_code == 200
        todo_item = response.json()
        assert todo_item["id"] == generated_todo_item["id"], "todo ID does not match"

    @pytest.mark.parametrize(
        "invalid_todo_id, expected_status_code, error_message",
        [
            (0, 422, "Input should be greater than 0"),
            ("a", 422, "Input should be a valid integer, unable to parse string as an integer"),
            (None, 422, "Input should be a valid integer"),
        ],
    )
    def test_get_todo_by_id_invalid_parameters(
        self,
        todo_url,
        authenticated_session,
        invalid_todo_id,
        expected_status_code,
        error_message,
    ):
        response = authenticated_session.get(f"{todo_url}/{invalid_todo_id}")
        assert response.status_code == expected_status_code
        assert error_message in response.text
