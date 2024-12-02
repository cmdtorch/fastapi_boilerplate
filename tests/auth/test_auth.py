import pytest
from httpx import AsyncClient


class TestSignup:
    @pytest.mark.parametrize(
        "request_data, excepted_code",
        [
            ("user_signin_data_not_exist_user", 400),
            ("user_signin_data_wrong", 401),
            ("user_signin_data", 200),
        ],
    )
    async def test_user_sign_in(
        self,
        request: pytest.FixtureRequest,
        ac: AsyncClient,
        request_data: str,
        excepted_code: int,
    ) -> None:
        content: str = request.getfixturevalue(request_data)
        response = await ac.post("/api/v1/auth/sign_in/", content=content)
        assert response.status_code == excepted_code
        response_data = response.json()
        if response.status_code == 200:
            assert (
                "access_token" in response_data
            ), "The key 'access_token' is missing in the response"
            assert (
                "refresh_token" in response_data
            ), "The key 'refresh_token' is missing in the response"
