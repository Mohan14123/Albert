from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from jose import jwt, JWTError

from app.config.settings import settings
from app.core.exceptions import AuthenticationError

# ---------------------------------------------------------
# Password Hashing (Argon2id)
# ---------------------------------------------------------
ph = PasswordHasher()


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


# ---------------------------------------------------------
# JWT (JSON Web Tokens)
# ---------------------------------------------------------
def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create a new JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret.get_secret_value(), 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_access_token(token: str) -> str:
    """
    Verify a JWT access token and return the subject (user ID).
    Raises AuthenticationError if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret.get_secret_value(), 
            algorithms=[settings.jwt_algorithm]
        )
        subject: str = payload.get("sub")
        if not subject:
            raise AuthenticationError("Token payload missing subject")
        return subject
    except JWTError as e:
        raise AuthenticationError("Could not validate credentials") from e


# ---------------------------------------------------------
# AES-256 Encryption (for OAuth Tokens)
# ---------------------------------------------------------
# Initialize fernet with the secret key (must be 32 URL-safe base64-encoded bytes)
def get_fernet() -> Fernet:
    """Get Fernet instance dynamically to pick up any settings changes."""
    key = settings.token_encryption_key.get_secret_value()
    # If the key is not 32 URL-safe base64-encoded bytes, this will raise ValueError in Fernet
    # Assuming the config validated it to be 44 chars (base64 of 32 bytes)
    # If it's a raw 32-byte string, we might need to encode it for Fernet.
    # Let's ensure it's a valid Fernet key.
    import base64
    if len(key) == 32:
        key = base64.urlsafe_b64encode(key.encode('utf-8')).decode('utf-8')
    return Fernet(key)


def encrypt_token(plain_token: str) -> str:
    """Encrypt an OAuth token using AES-256 (Fernet)."""
    f = get_fernet()
    return f.encrypt(plain_token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an OAuth token using AES-256 (Fernet)."""
    f = get_fernet()
    return f.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
