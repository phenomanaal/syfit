from database.interface.syfit import DatabaseInterface, RoutineDay

class Interface:
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
        session.close()
        return day

    def get_days_by_routine_id(self, routine_id: int):
        session = self.Session()
        routine_days = (
            session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).all()
        )
        session.close()

        return routine_days

    def reset_day_idxs(self, routine_id: int):
        routine_days = self.get_days_by_routine_id(routine_id)

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
            self.reset_day_idxs(routine_id)
            session.commit()
        session.close()

    def delete_days_by_routine_id(self, routine_id: int) -> None:
        session = self.Session()
        session.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).delete()
        session.commit()
        session.close()