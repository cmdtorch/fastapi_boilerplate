import httpx
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.schemas.auth import UserSocialData


class SocAuth:
    @classmethod
    def google(cls, token: str) -> UserSocialData | None:
        request = google_requests.Request()
        info = id_token.verify_oauth2_token(token, request, clock_skew_in_seconds=300)
        return UserSocialData(
            email=info["email"],
            full_name=f"{info['given_name']} {info['given_name']}",
        )

    @classmethod
    def apple(cls, token: str) -> UserSocialData | None:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return UserSocialData(
                email=payload.get("email"),
                full_name=f"{payload.get("givenName")} {payload.get("familyName")}",
            )
        except jwt.exceptions.PyJWTError:
            return None

    @classmethod
    def facebook(cls, token: str) -> UserSocialData | None:
        response = httpx.get(
            f"https://graph.facebook.com/me?access_token={token}&fields=id,first_name,last_name,email,picture",
        )
        response_json = response.json()
        return UserSocialData(
            email=response_json.get("email"),
            full_name=f"{response_json.get('first_name')} "
            f"{response_json.get('last_name')}",
        )
