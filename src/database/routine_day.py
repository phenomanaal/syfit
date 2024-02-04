from src.database import routine
from src.database.syfit import RoutineDay


class Interface(routine.Interface):
    def add_routine_day(self, routine_id: int, routine_day_name: str, day_of_week: str):
        routine_days = self.get_days_by_routine_id(routine_id)
        day_idxs = [d.day_idx for d in routine_days]
        if day_idxs == []:
            day_idx = 0
        else:
            day_idx = max(day_idxs) + 1
        day = RoutineDay(
            routine_id=routine_id,
            day_idx=day_idx,
            routine_day_name=routine_day_name,
            day_of_week=day_of_week,
        )

        session = self.Session()
        session.add(day)
        session.commit()
        session.refresh(day)
        session.close()
        return day

    def get_days_by_routine_id(self, routine_id: int):
        session = self.Session()
        routine_days = (
            session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).all()
        )
        session.close()

        return routine_days

    def get_routine_day_by_id(self, day_id: int):
        session = self.Session()

        routine_day = session.query(RoutineDay).filter(RoutineDay.id == day_id).first()

        session.close()

        return routine_day

    def get_routine_day_by_idx(self, routine_id: int, day_idx: int):
        session = self.Session()

        routine_day = (
            session.query(RoutineDay)
            .filter(RoutineDay.routine_id == routine_id)
            .filter(RoutineDay.day_idx == day_idx)
            .first()
        )

        session.close()

        return routine_day

    def edit_routine_day(self, day_id: int, **kwargs):
        session = self.Session()
        routine_day_update = {
            k: v
            for k, v in kwargs.items()
            if k in RoutineDay.__table__.columns and k != "id"
        }
        session.query(RoutineDay).filter(RoutineDay.id == day_id).update(
            routine_day_update
        )
        session.commit()

        routine_day = self.get_routine_day_by_id(day_id)

        session.close()

        return routine_day

    def reset_day_idxs(self, routine_id: int):
        routine_days = self.get_days_by_routine_id(routine_id)
        routine_days = sorted(routine_days, key=lambda x: x.day_idx)

        session = self.Session()

        for n, d in enumerate(routine_days):
            if d.day_idx != n:
                session.query(RoutineDay).filter(RoutineDay.id == d.id).update(
                    {"day_idx": n}
                )
        session.commit()
        session.close()

    def delete_day_by_id(self, day_id: int) -> None:
        session = self.Session()
        day = session.query(RoutineDay).filter(RoutineDay.id == day_id).first()
        if day:
            routine_id = day.routine_id
            session.delete(day)
            session.commit()
            self.reset_day_idxs(routine_id)
        session.close()

    def delete_days_by_routine_id(self, routine_id: int) -> None:
        self.delete_routine(routine_id)

        session = self.Session()
        session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).delete()
        session.commit()
        session.close()
