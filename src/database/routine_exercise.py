from src.database.common import RoutineExercise
from src.database import routine_day


class Interface(routine_day.Interface):

    def add_routine_exercise(
        self,
        day_id: int,
        exercise_id: int,
        num_sets: int = 3,
        default_reps: int = 10,
        default_time: float = None,
        warmup_schema: int = None,
        exercise_idx: int = None,
    ):
        routine_exercises = self.get_exercises_by_routine_day_id(day_id)
        exercise_idxs = [d.exercise_idx for d in routine_exercises]
        if exercise_idxs == []:
            exercise_idx = 0
        else:
            exercise_idx = max(exercise_idxs) + 1
        exercise = RoutineExercise(
            day_id=day_id,
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
        session.refresh(exercise)
        session.close()

        return exercise

    def get_exercises_by_routine_day_id(self, day_id: int):
        session = self.Session()
        routine_exercises = (
            session.query(RoutineExercise)
            .filter(RoutineExercise.day_id == day_id)
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
            .filter(RoutineExercise.day_id == routine_day_id)
            .filter(RoutineExercise.exercise_idx == exercise_idx)
            .first()
        )
        session.close()
        return routine_exercise

    def edit_routine_exercise(self, routine_exercise_id: int, **kwargs):
        session = self.Session()
        routine_exercise_update = {
            k: v
            for k, v in kwargs.items()
            if k in RoutineExercise.__table__.columns and k != "id"
        }
        session.query(RoutineExercise).filter(
            RoutineExercise.id == routine_exercise_id
        ).update(routine_exercise_update)
        session.commit()

        routine_day = self.get_routine_exercise_by_id(routine_exercise_id)

        session.close()

        return routine_day

    def reset_exercise_idxs(self, day_id: int):
        routine_exercises = self.get_exercises_by_routine_day_id(day_id)
        routine_exercises = sorted(routine_exercises, key=lambda x: x.exercise_idx)

        session = self.Session()

        for n, e in enumerate(routine_exercises):
            if e.exercise_idx != n:
                session.query(RoutineExercise).filter(
                    RoutineExercise.id == e.id
                ).update({"exercise_idx": n})
        session.commit()
        session.close()

    def delete_exercise_by_id(self, routine_exercise_id: int) -> None:
        session = self.Session()
        exercise = (
            session.query(RoutineExercise)
            .filter(RoutineExercise.id == routine_exercise_id)
            .first()
        )
        if exercise:
            day_id = exercise.day_id
            session.delete(exercise)
            session.commit()
            self.reset_exercise_idxs(day_id)
        session.close()

    def delete_exercises_by_day_id(self, day_id: int) -> None:
        self.delete_day_by_id(day_id)

        session = self.Session()
        session.query(RoutineExercise).filter(RoutineExercise.day_id == day_id).delete()
        session.commit()
        session.close()
