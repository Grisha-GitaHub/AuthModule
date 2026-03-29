import bcrypt
import jwt as pyjwt
from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str | None = None,
    algorithm: str | None = None
) -> str:
    if private_key is None:
        private_key = settings.auth_JWT.private_key_path.read_text()
    if algorithm is None:
        algorithm = settings.auth_JWT.algorithm
    encoded = pyjwt.encode(
        payload,
        private_key,
        algorithm=algorithm
    )
    return encoded


def decoded_jwt(
    token: str | bytes,
    public_key: str | None = None,
    algorithm: str | None = None
) -> dict:
    if public_key is None:
        public_key = settings.auth_JWT.public_key_path.read_text()
    if algorithm is None:
        algorithm = settings.auth_JWT.algorithm
    decoded = pyjwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(password: str, hashed_password: str | bytes) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bool(bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    ))  
