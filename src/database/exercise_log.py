from datetime import datetime, timedelta
from sqlalchemy import and_
from src.database.syfit import ExerciseLog, User, Routine, RoutineDay, RoutineExercise
from src.database import routine_exercise


class Interface(routine_exercise.Interface):

    def add_log(
        self,
        routine_exercise_id: int,
        time_stamp: datetime,
        num_reps: int = None,
        time_duration: float = None,
    ):
        exercises = self.get_exercise_logs_by_routine_exercise_id(routine_exercise_id)
        set_idxs = [
            e.set_idx
            for e in exercises
            if e.time_stamp >= (time_stamp + timedelta(minutes=-60))
            and e.time_stamp <= (time_stamp + timedelta(minutes=60))
        ]

        if len(set_idxs) == 0:
            set_idx = 0
        else:
            set_idx = max(set_idxs) + 1
        exercise = ExerciseLog(
            routine_exercise_id=routine_exercise_id,
            time_stamp=time_stamp,
            set_idx=set_idx,
            num_reps=num_reps,
            time_duration=time_duration,
        )

        session = self.Session()
        session.add(exercise)
        session.commit()
        session.refresh(exercise)
        session.close()

        return exercise

    def get_exercise_logs_by_routine_exercise_id(self, routine_exercise_id: int):
        session = self.Session()
        exercises = (
            session.query(ExerciseLog)
            .filter(ExerciseLog.routine_exercise_id == routine_exercise_id)
            .all()
        )
        session.close()

        return exercises

    def get_exercise_log_by_id(self, exercise_log_id: int):
        session = self.Session()
        exercise_log = (
            session.query(ExerciseLog).filter(ExerciseLog.id == exercise_log_id).first()
        )
        session.close()
        return exercise_log

    def get_exercise_log_by_set(self, routine_exercise_id: int, set_idx: int):
        session = self.Session()
        exercise_log = (
            session.query(ExerciseLog)
            .filter(
                and_(
                    ExerciseLog.routine_exercise_id == routine_exercise_id,
                    ExerciseLog.set_idx == set_idx,
                )
            )
            .first()
        )
        session.close()
        return exercise_log

    def get_exercise_logs_by_user(self, user_id: int):
        session = self.Session()
        logs = (
            session.query(ExerciseLog)
            .join(RoutineExercise)
            .join(RoutineDay)
            .join(Routine)
            .filter(Routine.user_id == user_id)
            .all()
        )
        session.close()
        return logs

    def get_exercise_logs_by_routine_exercise(self, routine_exercise_id: int):
        session = self.Session()
        logs = (
            session.query(ExerciseLog)
            .join(RoutineExercise)
            .filter(RoutineExercise.id == routine_exercise_id)
            .all()
        )
        session.close()
        return logs

    def get_exercise_logs_by_routine_day(self, routine_day_id: int):
        session = self.Session()
        logs = (
            session.query(ExerciseLog)
            .join(RoutineExercise)
            .join(RoutineDay)
            .filter(RoutineDay.id == routine_day_id)
            .all()
        )
        session.close()
        return logs

    def get_exercise_logs_by_routine(self, routine_id: int):
        session = self.Session()
        logs = (
            session.query(ExerciseLog)
            .join(RoutineExercise)
            .join(RoutineDay)
            .join(Routine)
            .filter(Routine.id == routine_id)
            .all()
        )
        session.close()
        return logs

    def edit_exercise_log(self, exercise_log_id: int, **kwargs):
        session = self.Session()
        exercise_log_update = {
            k: v
            for k, v in kwargs.items()
            if k in ExerciseLog.__table__.columns and k != "id"
        }

        session.query(ExerciseLog).filter(ExerciseLog.id == exercise_log_id).update(
            exercise_log_update
        )
        session.commit()
        session.close()

        exercise_log = self.get_exercise_log_by_id(exercise_log_id)

        return exercise_log

    def reset_set_idxs(self, routine_exercise_id: int):
        exercise_logs = self.get_exercise_logs_by_routine_exercise_id(
            routine_exercise_id
        )
        exercise_logs = sorted(exercise_logs, key=lambda x: x.set_idx)

        session = self.Session()

        for n, e in enumerate(exercise_logs):
            if e.set_idx != n:
                session.query(ExerciseLog).filter(ExerciseLog.id == e.id).update(
                    {"set_idx": n}
                )
        session.commit()
        session.close()

    def delete_exercise_log_by_id(self, exercise_log_id: int) -> None:
        session = self.Session()
        exercise_log = (
            session.query(ExerciseLog).filter(ExerciseLog.id == exercise_log_id).first()
        )
        if exercise_log:
            routine_exercise_id = exercise_log.routine_exercise_id
            session.delete(exercise_log)
            session.commit()
            self.reset_set_idxs(routine_exercise_id)
        session.close()

    def delete_exercises_by_routine_exercise_id(self, routine_exercise_id: int) -> None:
        self.delete_exercise_by_id(routine_exercise_id)

        session = self.Session()
        session.query(ExerciseLog).filter(
            ExerciseLog.routine_exercise_id == routine_exercise_id
        ).delete()
        session.commit()
        session.close()
