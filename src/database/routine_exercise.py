from sqlalchemy.orm import and_
from src.database.syfit import DatabaseInterface, RoutineExercise


class Interface(DatabaseInterface):

    def add_routine_exercise(
        self,
        routine_day_id: int,
        exercise_id: int,
        exercise_idx: int,
        num_sets: int,
        default_reps: int,
        default_time: float,
        warmup_schema: int,
    ):
        routine_exercises = self.get_exercises_by_routine_day_id(routine_day_id)
        exercise_idxs = [d.exercise_idx for d in routine_exercises]
        if exercise_idxs == []:
            exercise_idx = 0
        else:
            exercise_idx = max(exercise_idxs) + 1
        exercise = RoutineExercise(
            routine_day_id=routine_day_id,
            exercise_id=exercise_id,
            exercise_idx=exercise_idx,
            num_sets=num_sets,
            default_reps=default_reps,
            default_time=default_time,
            warmup_schema=warmup_schema,
        )

        session = self.Session()
        session.add(exercise)
        session.commit()
        session.close()

        return exercise

    def get_exercises_by_routine_day_id(self, day_id: int):
        session = self.Session()
        routine_exercises = (
            session.query(RoutineExercise)
            .filter(RoutineExercise.routine_day_id == day_id)
            .all()
        )
        session.close()

        return routine_exercises

    def get_routine_exercise_by_id(self, routine_exercise_id: int):
        session = self.Session()
        routine_exercise = (
            session.query(RoutineExercise)
            .filter(RoutineExercise.id == routine_exercise_id)
            .first()
        )
        session.close()

        return routine_exercise

    def get_routine_exercise_by_idx(self, routine_day_id: int, exercise_idx: int):
        session = self.Session()
        routine_exercise = (
            session.query(RoutineExercise)
            .filter(
                and_(
                    RoutineExercise.day_id == routine_day_id,
                    RoutineExercise.exercise_idx == exercise_idx,
                )
            )
            .first()
        )
        session.close()
        return routine_exercise
    
    def edit_routine_exercise(self, routine_exercise_id: int, **kwargs):
        session = self.Session()
        routine_day_update = {
            k: v
            for k, v in kwargs.items()
            if k in RoutineExercise.__table__.columns and k != "id"
        }
        session.query(RoutineExercise).filter(RoutineExercise.id == routine_exercise_id).update(
            routine_day_update
        )
        session.commit()

        routine_day = self.get_routine_exercise_by_id(routine_exercise_id)

        session.close()

        return routine_day

    def reset_exercise_idx(self, day_id: int):
        routine_exercises = self.get_exercises_by_routine_day_id(day_id)

        session = self.Session()

        for n, e in enumerate(routine_exercises):
            if e.exercise_idx != n:
                session.query(RoutineExercise).filter(
                    RoutineExercise.id == e.id
                ).update({"exercise_idx": n})
        session.commit()
        session.close()
