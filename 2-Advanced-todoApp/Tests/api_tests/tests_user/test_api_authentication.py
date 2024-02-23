import pytest
import requests


class TestUserAuthentication:
    def test_authentication(self, auth_token_body_response):
        empty_list_of_elements = ["", None, False]
        response_keys_list = {"access_token", "token_type"}

        try:
            for response_key in response_keys_list:
                assert (
                    auth_token_body_response[response_key] not in empty_list_of_elements
                ), f"{response_key} failed to be retrieved"
        except TypeError as e:
            raise Exception(f"Failed to retrieve the access token: {repr(e)}")
        except KeyError as e:
            raise KeyError(f"Failed to retrieve the expected key: {repr(e)}")

    @pytest.mark.parametrize(
        "field, value, error_message, status_code",
        [
            ("username", "", "Field required", 422),
            ("username", "wrong_user", "Could not validate credentials", 401),
            ("password", "", "Field required", 422),
            ("password", "wrong_user", "Could not validate credentials", 401),
        ],
    )
    def test_authentication_invalid_parameters(
        self, auth_url, basic_auth_token_body, field, value, error_message, status_code
    ):
        basic_auth_token_body = {**basic_auth_token_body, field: value}
        response = requests.post(f"{auth_url}/token", data=basic_auth_token_body)
        assert response.status_code == status_code
        assert error_message in response.text
