from fastapi import APIRouter, Depends, Request
import json
from src.database.syfit import Syfit, get_db
from datetime import datetime

router = APIRouter()


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


@router.put("/measurement/{measurement_id}/edit")
async def edit_measurement(
    measurement_id: int, request: Request, db: Syfit = Depends(get_db)
):
    kwargs = json.loads((await request.body()).decode())
    return db.measurement.edit_measurement(measurement_id, **kwargs)


@router.put("/measurement/user/{user_id}/change_measurement_system")
async def change_measurement_system(
    user_id: int, request: Request, db: Syfit = Depends(get_db)
):
    change_values = json.loads((await request.body()).decode())["change_values"]
    db.measurement.change_measurement_system(user_id, change_values)


@router.delete("/measurement/{measurement_id}/delete")
async def delete_measurement(measurement_id: int, db: Syfit = Depends(get_db)):
    db.measurement.delete_measurement(measurement_id)


@router.delete("/measurement/user/{user_id}/delete")
async def delete_measurements_for_user(user_id: int, db: Syfit = Depends(get_db)):
    db.measurement.delete_all_measurements_by_user(user_id)
