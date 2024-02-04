from typing import List
from src.database.syfit import DatabaseInterface, Routine


class Interface(DatabaseInterface):
    def add_routine(
        self, user_id: int, routine_name: str, num_days: int, is_current: bool = None
    ) -> Routine:
        any_routines = len(self.get_all_user_routines(user_id)) > 0

        if is_current is None:
            if not any_routines:
                is_current = True
            else:
                is_current = False

        routine = Routine(
            user_id=user_id,
            routine_name=routine_name,
            num_days=num_days,
            is_current=is_current,
        )

        session = self.Session()
        session.add(routine)
        session.commit()
        session.refresh(routine)
        session.close()

        return routine

    def get_all_user_routines(self, user_id: int) -> List[Routine]:
        session = self.Session()
        routines = session.query(Routine).filter(Routine.user_id == user_id).all()
        session.close()

        return routines

    def get_routine_by_id(self, routine_id: int) -> Routine:
        session = self.Session()
        routine = session.query(Routine).filter(Routine.id == routine_id).first()
        session.close()

        return routine

    def edit_routine(self, routine_id: int, **kwargs):
        session = self.Session()
        routine_update = {
            k: v
            for k, v in kwargs.items()
            if k in ["routine_name", "num_days"] and k in Routine.__table__.columns
        }
        session.query(Routine).filter(Routine.id == routine_id).update(routine_update)
        session.commit()

        routine = self.get_routine_by_id(routine_id)

        session.close()

        return routine

    def make_routine_not_current(self, routine_id: int) -> None:
        session = self.Session()
        session.query(Routine).filter(Routine.id == routine_id).update(
            {"is_current": False}
        )
        session.commit()
        routine = self.get_routine_by_id(routine_id)
        session.close()
        return routine

    def make_routine_current(self, routine_id: int):
        session = self.Session()
        routine = self.get_routine_by_id(routine_id)
        user_id = routine.user_id
        routine_ids = [
            r.id for r in self.get_all_user_routines(user_id) if r != routine_id
        ]

        for i in routine_ids:
            self.make_routine_not_current(i)

        session.query(Routine).filter(Routine.id == routine_id).update(
            {"is_current": True}
        )

        session.commit()
        session.close()

        routine = self.get_routine_by_id(routine_id)

        return routine

    def delete_routine(self, routine_id: int) -> None:
        session = self.Session()
        routine = self.get_routine_by_id(routine_id)

        if routine:
            session.delete(routine)
            session.commit()

        session.close()
