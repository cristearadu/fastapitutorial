import pytest


class TestTodosDelete:
    @pytest.mark.dependency(depeonds=["test_create_todo"])
    def test_delete_todo(self, generated_todo_item):
        pass

    @pytest.mark.parametrize(
        "invalid_todo_id, expected_status_code, error_message",
        [
            (0, 422, "Input should be greater than 0"),
            ("a", 422, "Input should be a valid integer, unable to parse string as an integer"),
            (1.5, 422, "Input should be a valid integer")
        ],
    )
    def test_delete_book_invalid_parameters(
        self,
        todo_url,
        authenticated_session,
        invalid_todo_id,
        expected_status_code,
        error_message,
    ):
        response = authenticated_session.delete(f"{todo_url}/{invalid_todo_id}")
        assert response.status_code == expected_status_code
        assert error_message in response.text
