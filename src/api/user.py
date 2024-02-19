from typing import Annotated
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from src.database.syfit import Syfit
from src.database.common import User
from src import config
from src.api import auth


class RequestUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    password: str | None
    DOB: str
    last_updated_username: datetime
    measurement_system: str


router = APIRouter(dependencies=[Depends(auth.validate_api_key)])
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = Syfit(config.config["DATABASE"]["CONN_STRING"])
    try:
        yield db
    finally:
        db.Session().close()


@router.get("/users/")
async def read_users(token: str = Depends(oauth2_scheme), db: Syfit = Depends(get_db)):
    token_data = auth.get_token_data(token)
    if token_data.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized."
        )
    return db.user.get_all_users()


@router.get("/users/id/{user_id}")
async def get_user_by_id(
    user_id: int, token: str = Depends(oauth2_scheme), db: Syfit = Depends(get_db)
):
    token_data = auth.get_token_data(token)
    user = db.user.get_user_by_id(user_id)

    if user is None:
        raise auth.credentials_exception
    elif user.username != token_data.username:
        raise auth.credentials_exception

    response_user = RequestUser(**user.to_model_dict())
    return response_user


@router.get("/users/username/{username}")
async def get_user_by_username(
    username: str, token: str = Depends(oauth2_scheme), db: Syfit = Depends(get_db)
) -> RequestUser | None:
    token_data = auth.get_token_data(token)
    user = db.user.get_user_by_username(username)

    if user is None:
        raise auth.credentials_exception
    elif user.username != token_data.username:
        raise auth.credentials_exception

    response_user = RequestUser(**user.to_model_dict())
    return response_user


@router.post("/users/signup/")
async def signup(
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    email: Annotated[str, Form()],
    DOB: Annotated[str, Form()],
    measurement_system: Annotated[str, Form()],
    db: Syfit = Depends(get_db),
):
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=password,
        email=email,
        DOB=DOB,
        measurement_system=measurement_system,
    )
    str_password = user.password
    user.password = password_context.hash(user.password)
    user.DOB = datetime.strptime(user.DOB, "%m/%d/%Y").date()
    user = db.user.add_user(user)
    if isinstance(user, dict):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=user.get("message")
        )
    data = OAuth2PasswordRequestForm(username=user.username, password=str_password)
    return await login_for_access_token(form_data=data, db=db)


@router.post("/users/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Syfit = Depends(get_db),
) -> auth.Token:
    user = auth.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(config.config["API"]["ACCESS_TOKEN_EXPIRE_MINUTES"])
    )
    subject = f"username:{user.username},id:{user.id}"
    access_token = auth.create_access_token(
        data={"sub": subject}, expires_delta=access_token_expires
    )
    return auth.Token(access_token=access_token, token_type="bearer")


@router.put("/users/id/{user_id}/edit")
async def change_username_by_id(
    user_id: int,
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Syfit = Depends(get_db),
):
    token_data = auth.get_token_data(token)
    if user_id != token_data.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized."
        )
    username = json.loads((await request.body()).decode())["username"]
    return db.user.change_username_by_id(user_id, username)


@router.delete("/users/id/{user_id}/delete")
async def delete_username(
    user_id: int, token: str = Depends(oauth2_scheme), db: Syfit = Depends(get_db)
):
    token_data = auth.get_token_data(token)
    if user_id != token_data.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized."
        )
