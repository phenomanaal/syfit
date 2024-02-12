from typing import Annotated
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from src.database.syfit import Syfit
from src.database.common import User
from src import config
from src.api import auth


class RequestUser:
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    DOB: str
    last_updated_username: datetime
    measurement_system: str


router = APIRouter()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = Syfit(config.config["DATABASE"]["CONN_STRING"])
    try:
        yield db
    finally:
        db.Session().close()


@router.get("/users/")
async def read_users(db: Syfit = Depends(get_db)):
    return db.user.get_all_users()


@router.get("/users/id/{user_id}")
async def get_user_by_id(user_id: int, db: Syfit = Depends(get_db)):
    return db.user.get_user_by_id(user_id)


@router.get("/users/username/{username}")
async def get_user_by_username(username: str, db: Syfit = Depends(get_db)):
    return db.user.get_user_by_username(username)


@router.post("/users/signup/")
async def signup(
    user: Request,
    db: Syfit = Depends(get_db),
):
    user = json.loads((await user.body()).decode())
    user["password"] = password_context.hash(user["password"])
    user["DOB"] = datetime.strptime(user["DOB"], "%m/%d/%Y").date()
    user = User(**user)
    user = db.user.add_user(user)
    return user.id


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
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return auth.Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/")
async def read_users_me(
    current_user: RequestUser = Depends(auth.get_current_user),
):
    return current_user


@router.put("/users/id/{user_id}/edit")
async def change_username_by_id(
    user_id: int, request: Request, db: Syfit = Depends(get_db)
):
    username = json.loads((await request.body()).decode())["username"]
    return db.user.change_username_by_id(user_id, username)


@router.delete("/users/id/{user_id}/delete")
async def delete_username(user_id: int, db: Syfit = Depends(get_db)):
    db.user.delete_user(user_id)
