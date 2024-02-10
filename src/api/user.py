from fastapi import APIRouter
from src.database.syfit import Syfit
from src.database.common import User
from src import config

router = APIRouter()
db = Syfit(config.config["DATABASE"]["CONN_STRING"])


@router.get("/users/")
async def read_users():
    return db.user.get_all_users()


@router.get("/users/id/{user_id}")
async def get_user_by_id(user_id: int):
    return db.user.get_user_by_id(user_id)


@router.get("/users/username/{username}")
async def get_user_by_username(username: str):
    return db.user.get_user_by_username(username)


@router.post("/users/")
async def add_user(user: User):
    db.user.add_user(**user)
