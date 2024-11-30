import httpx
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.schemas.auth import SocUserInfo


class SocAuth:
    @classmethod
    def google(cls, token: str) -> SocUserInfo | None:
        request = google_requests.Request()
        info = id_token.verify_oauth2_token(token, request, clock_skew_in_seconds=300)
        return SocUserInfo(
            email=info["email"],
            full_name=f"{info['given_name']} {info['given_name']}",
        )

    @classmethod
    def apple(cls, token: str) -> SocUserInfo | None:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return SocUserInfo(
                email=payload.get("email"),
                full_name=f"{payload.get("givenName")} {payload.get("familyName")}",
            )
        except jwt.exceptions.PyJWTError:
            return None

    @classmethod
    def facebook(cls, token: str) -> SocUserInfo | None:
        response = httpx.get(
            f"https://graph.facebook.com/me?access_token={token}&fields=id,first_name,last_name,email,picture",
        )
        response_json = response.json()
        return SocUserInfo(
            email=response_json.get("email"),
            full_name=f"{response_json.get('first_name')} "
            f"{response_json.get('last_name')}",
        )
