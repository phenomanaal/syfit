from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from src.database.syfit import Syfit
from src import config

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_db():
    db = Syfit(config.config["DATABASE"]["CONN_STRING"])
    try:
        yield db
    finally:
        db.Session().close()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    id: int | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def payload_to_token_data(payload_sub: str) -> TokenData:
    payload_sub = payload_sub.split(",")
    username = payload_sub[0].split(":")[1]
    id = payload_sub[1].split(":")[1]
    return TokenData(username=username, id=id)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Syfit = Depends(get_db)):
    user = db.user.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_token_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            config.config["API"]["API_KEY"],
            algorithms=[config.config["API"]["ALGORITHM"]],
        )
        payload_sub: str = payload.get("sub")
        token_data = payload_to_token_data(payload_sub)
        if token_data.username is None or token_data.id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return token_data


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.config["API"]["API_KEY"],
        algorithm=config.config["API"]["ALGORITHM"],
    )
    return encoded_jwt
