import os

import pytest

from app.core.schemas.auth import SignIn

test_firebase_token = os.getenv("TEST_FIREBASE_TOKEN", "default_firebase_token")
test_password = os.getenv("TEST_PASSWORD", "default_password")
test_wrong_password = os.getenv("TEST_WRONG_PASSWORD", "default_wrong_password")


@pytest.fixture
def user_signin_data() -> str:
    return SignIn(
        email="consumer@example.com",
        password=test_password,
        firebase_token=test_firebase_token,
        timezone="UTC",
    ).model_dump_json()


@pytest.fixture
def user_signin_data_wrong() -> str:
    return SignIn(
        email="consumer@example.com",
        password=test_wrong_password,
        firebase_token=test_firebase_token,
        timezone="UTC",
    ).model_dump_json()


@pytest.fixture
def user_signin_data_not_exist_user() -> str:
    return SignIn(
        email="notexist@example.com",
        password=test_password,
        firebase_token=test_firebase_token,
        timezone="UTC",
    ).model_dump_json()
