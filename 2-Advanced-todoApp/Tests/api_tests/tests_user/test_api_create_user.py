import requests
import pytest


class TestUserCreation:
    @pytest.mark.dependency()
    def test_user_creation(self, user_creation_and_deletion):
        pass

    @pytest.mark.parametrize(
        "field, value, error_message",
        [
            (["username", "first_name", "last_name"], "a", "String should have at least 2 characters"),
            (["username", "first_name", "last_name"], "", "String should have at least 2 characters"),
            (["username", "first_name", "last_name"], 1, "Input should be a valid string"),
            (["username", "first_name", "last_name"], 1.1, "Input should be a valid string"),
            (["username", "first_name", "last_name"], True, "Input should be a valid string"),
            (["username", "first_name", "last_name"], False, "Input should be a valid string"),
            (["username", "first_name", "last_name"], None, "Input should be a valid string"),
            ("email", "not_an-email", "The email address is not valid. It must have exactly one @-sign."),
            ("email", "funny_domain@domain.whatever", "Invalid email domain!"),
            ("email", "Michael BrooksLaura Patel@gmail.com",
             "The email address contains invalid characters before the @-sign: SPACE"),
            ("role", "anything", "Invalid role type")
        ],
    )
    def test_user_creation_invalid_parameters(self, auth_url, user_creation_and_deletion, random_auth_user_body_data,
                                              field, value, error_message):
        fields_to_test = field if isinstance(field, list) else [field]

        for test_field in fields_to_test:
            auth_body_data = {**random_auth_user_body_data, test_field: value}
            response = requests.post(f"{auth_url}", json=auth_body_data)
            assert response.status_code == 422
            assert error_message in response.text

    @pytest.mark.parametrize(
        "field, error_message",
        [
            ("username", "Username Already Registered"),
            ("email", "Email Address Already Registered"),
        ],
    )
    def test_user_registration_with_duplicate_data(self, auth_url, user_creation_and_deletion,
                                                   generate_user_data, field, error_message):
        user_data = {
            ** generate_user_data,
            field: user_creation_and_deletion[field]
        }
        response = requests.post(auth_url, json=user_data)
        assert response.status_code == 400
        assert error_message in response.text
