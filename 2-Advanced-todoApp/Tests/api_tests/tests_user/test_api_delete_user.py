import pytest


class TestUserDeletion:

    @pytest.mark.dependency(depeonds=["test_user_creation"])
    def test_user_deletion(self):
        pass

    @pytest.mark.parametrize(
        "field, value, error_code, error_message",
        [
            ("password", "", 401, "Passwords do not match!"),
            ("password", "random_pass", 401, "Passwords do not match!"),
            ("password", 1, 422, "Input should be a valid string"),
            ("password", None, 422, "Input should be a valid string"),
        ],
    )
    def test_user_deletion_invalid_data(self, user_url, user_creation_and_deletion, random_auth_user_body_data,
                                        authenticated_session, field, value, error_code, error_message):
        detele_body_data = {**random_auth_user_body_data,
                             field: value}
        response = authenticated_session.delete(user_url, json=detele_body_data)
        assert response.status_code == error_code
        assert error_message in response.text


