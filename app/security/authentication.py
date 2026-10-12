import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import jwt

load_dotenv()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")


def create_access_token(username: str) -> str:
    """
    Create a signed JWT containing the authenticated username.
    """

    expiration_minutes = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=expiration_minutes)

    payload = {
        "sub": username,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    """
    Validate a JWT and return the authenticated username.

    Raises jwt.InvalidTokenError for invalid or expired tokens.
    """

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    username = payload.get("sub")

    if not username or not isinstance(username, str):
        raise jwt.InvalidTokenError(
            "Token does not contain a valid subject."
        )

    return username.strip()