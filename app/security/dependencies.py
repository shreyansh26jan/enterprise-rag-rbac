from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.security.authentication import decode_access_token


security = HTTPBearer()


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Authenticate the request and return the trusted username
    extracted from the validated JWT.
    """

    token = credentials.credentials

    try:
        username = decode_access_token(token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username