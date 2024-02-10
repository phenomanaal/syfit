from fastapi import APIRouter, Depends, Request
import json
from src.database.syfit import Syfit
from src.database.common import User
from src import config
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()


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


@router.post("/users/")
async def add_user(request: Request, db: Syfit = Depends(get_db)):
    user = json.loads((await request.body()).decode())
    user["DOB"] = datetime.strptime(user["DOB"], "%m/%d/%Y").date()
    user = db.user.add_user(**user)
    return user.id


@router.put("/users/id/{user_id}/edit")
async def change_username_by_id(
    user_id: int, request: Request, db: Syfit = Depends(get_db)
):
    username = json.loads((await request.body()).decode())["username"]
    return db.user.change_username_by_id(user_id, username)


@router.delete("/users/id/{user_id}/delete")
async def delete_username(user_id: int, db: Syfit = Depends(get_db)):
    db.user.delete_user(user_id)
