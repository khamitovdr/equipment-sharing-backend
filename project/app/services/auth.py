import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.crud.users import get_user_by_email
from app.models.users import User
from app.schemas.auth import TokenDataSchema

ALGORITHM = "HS256"
# to get a string like this run:
# openssl rand -hex 32
secret_key = get_settings().secret_key


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


log = logging.getLogger("uvicorn")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str) -> User or bool:
    if email is None or password is None:
        return False
    user = await get_user_by_email(email)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    log.info(f"Getting current user by token {token[:10]}...")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        log.info(f"Current user email: {email}")
        if email is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenDataSchema(email=email)
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    user = await get_user_by_email(email=token_data.email)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    log.info(f"Getting current active user {current_user.email}...")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
