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


@router.get("/measurement/user/{user_id}")
async def get(user_id: int, db: Syfit = Depends(get_db)):
    return db.measurement.get_all_measurement_by_user(user_id)


@router.get("/measurement/user/{user_id}/latest")
async def get_latest_measurement_by_user(user_id: int, db: Syfit = Depends(get_db)):
    return db.measurement.get_latest_measurement_by_user(user_id)


@router.get("/measurement/{measurement_id}")
async def get_measurement_by_id(measurement_id: int, db: Syfit = Depends(get_db)):
    return db.measurement.get_measurement_by_id(measurement_id)


@router.get("/measurement/user/{user_id}/time")
async def get_measurements_by_date(
    user_id: int,
    start_time: str,
    end_time: str = datetime.utcnow(),
    db: Syfit = Depends(get_db),
):
    start_time = datetime.strptime(start_time, "%Y%m%d")
    if not isinstance(end_time, datetime):
        end_time = datetime.strptime(end_time, "%Y%m%d")
    return db.measurement.get_all_measurements_by_user_by_date(
        user_id, start_time, end_time
    )