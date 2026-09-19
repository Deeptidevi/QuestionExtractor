from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
from jose import jwt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hashed version."""
    if not plain_password or not hashed_password:
        return False
    try:
        # bcrypt requires bytes
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate a secure bcrypt hash for a password."""
    # Truncate to 72 bytes per bcrypt standard
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(subject),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except Exception:
        return None
