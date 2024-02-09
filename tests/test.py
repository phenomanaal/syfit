from datetime import datetime, timedelta
import math
from sqlalchemy import and_
from src.database import (
    user,
    syfit,
    measurement,
    routine,
    routine_day,
    exercise,
    routine_exercise,
    exercise_log,
)
import src.config as config

conn_string = config.config.get("DATABASE", "CONN_STRING")

db_interface = syfit.DatabaseInterface(conn_string, restart_db=True)
user_interface = user.Interface(conn_string)
measurement_interface = measurement.Interface(conn_string)
routine_interface = routine.Interface(conn_string)
routine_day_interface = routine_day.Interface(conn_string)
exercise_interface = exercise.Interface(conn_string)
routine_exercise_interface = routine_exercise.Interface(conn_string)
exercise_log_interface = exercise_log.Interface(conn_string)


class TestUser:
    def test_add_user(self):
        add_user = user_interface.add_user(
            "Test",
            "User",
            "testuser2023",
            datetime.strptime("1/25/2023", "%m/%d/%Y").date(),
            "imperial",
        )

        session = user_interface.Session()
        get_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "testuser2023")
            .first()
        )

        assert add_user.id == get_user.id
        assert add_user.first_name == get_user.first_name
        assert add_user.last_name == get_user.last_name
        assert add_user.username == get_user.username
        assert add_user.DOB == get_user.DOB
        assert add_user.last_updated_username == get_user.last_updated_username
        assert add_user.measurement_system == get_user.measurement_system

        session.commit()
        session.close()

    def test_add_duplicate_username(self):
        duplicate_user = user_interface.add_user(
            "NewTest", "User", "testuser2023", datetime.utcnow().date(), "metric"
        )

        session = user_interface.Session()

        get_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "testuser2023")
            .all()
        )

        assert isinstance(duplicate_user, str)
        assert len(get_user) == 1
        assert get_user[0].username == "testuser2023"
        assert get_user[0].first_name != "NewTest"

        session.commit()
        session.close()

    def test_get_all_users(self):
        users = user_interface.get_all_users()

        assert len(users) == 1

        test_user = users[0]
        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"

    def test_get_user_by_id(self):
        test_user = user_interface.get_user_by_id(1)

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_id(23424234) is None

    def test_get_user_by_username(self):
        test_user = user_interface.get_user_by_username("testuser2023")

        assert test_user.id == 1
        assert test_user.first_name == "Test"
        assert test_user.last_name == "User"
        assert test_user.username == "testuser2023"
        assert test_user.DOB == datetime.strptime("1/25/2023", "%m/%d/%Y").date()
        assert test_user.measurement_system == "imperial"
        assert user_interface.get_user_by_username("asdf") is None

    def test_change_username_by_id(self):
        user_ = user_interface.change_username_by_id(1, "newusername23")

        session = user_interface.Session()

        test_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "newusername23")
            .first()
        )

        user_ = session.query(syfit.User).filter(syfit.User.id == 1).first()

        session.close()

        assert test_user is None
        assert user_ is not None
        assert user_.username == "testuser2023"

    def test_change_username_by_username(self):
        user_ = user_interface.change_username_by_username(
            "testuser2023", "newusername23"
        )

        session = user_interface.Session()

        test_user = (
            session.query(syfit.User)
            .filter(syfit.User.username == "newusername23")
            .first()
        )

        user_ = session.query(syfit.User).filter(syfit.User.id == 1).first()

        session.close()

        assert test_user is None
        assert user_ is not None
        assert user_.username == "testuser2023"

        # TODO: wait 24 hours from when testuser2023 was added and try again but this time assert that the username has changed


class TestMeasurement:
    def test_add_measurement(self):
        session = measurement_interface.Session()

        measurement_interface.add_measurement(1, None, height=60, body_weight=125)

        test_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 1).first()
        )

        assert test_measurement is not None
        assert test_measurement.height == 60
        assert test_measurement.body_weight == 125
        assert test_measurement.user_id == 1

    def test_get_all_measurements_by_user(self):
        user_id = 1

        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-120), body_weight=150
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-100), body_weight=145
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-80), body_weight=140
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-60), body_weight=135
        )
        measurement_interface.add_measurement(
            user_id, datetime.utcnow() + timedelta(days=-30), body_weight=130
        )

        measurements = measurement_interface.get_all_measurement_by_user(user_id)
        body_weights = [m.body_weight for m in measurements]

        session = measurement_interface.Session()

        query_measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.user_id == user_id)
            .all()
        )
        query_body_weights = [m.body_weight for m in query_measurements]

        assert len(measurements) == len(query_measurements)
        assert max(body_weights) == max(query_body_weights)
        assert min(body_weights) == min(query_body_weights)

    def test_get_all_measurements_by_user_by_date(self):
        start_time = (datetime.utcnow() + timedelta(days=-120)).date()
        end_time = (datetime.utcnow() + timedelta(days=-59)).date()

        session = measurement_interface.Session()

        measurements = measurement_interface.get_all_measurements_by_user_by_date(
            1, start_time, end_time
        )

        query_measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.measurement_time >= start_time)
            .filter(syfit.Measurement.measurement_time < end_time)
            .all()
        )

        assert len(measurements) == len(query_measurements)

    def test_get_latest_measurement_by_user(self):
        latest = measurement_interface.get_latest_measurement_by_user(1)

        measurement_times = [
            m.measurement_time
            for m in measurement_interface.get_all_measurement_by_user(1)
        ]
        latest_query = max(measurement_times)

        assert latest.measurement_time == latest_query

    def test_get_measurement_by_measurement(self):
        session = measurement_interface.Session()

        measurements = measurement_interface.get_measurement_by_measurements(
            user_id=1, body_weight=125
        )

        assert len(measurements) == 1

        measurement = measurements[0]

        query_measurement = (
            session.query(syfit.Measurement)
            .filter(
                syfit.Measurement.user_id == 1, syfit.Measurement.body_weight == 125
            )
            .first()
        )

        assert measurement.user_id == query_measurement.id
        assert measurement.body_weight == query_measurement.body_weight
        assert measurement.height == query_measurement.height

        measurement_interface.add_measurement(
            1, datetime.utcnow() + timedelta(days=30), body_weight=130
        )

        measurements = measurement_interface.get_measurement_by_measurements(
            user_id=1, body_weight=130
        )

        assert len(measurements) == 2

    def test_get_measurement_by_id(self):
        session = measurement_interface.Session()
        measurement = measurement_interface.get_measurement_by_id(1)

        query_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 1).first()
        )

        assert measurement.id == query_measurement.id
        assert measurement.user_id == query_measurement.user_id
        assert measurement.height == query_measurement.height
        assert measurement.body_weight == query_measurement.body_weight

    def test_edit_measurement(self):
        measurement_interface.edit_measurement(
            7, measurement_time=datetime.utcnow() + timedelta(days=-10), body_weight=127
        )

        session = measurement_interface.Session()

        query_measurement = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 7).first()
        )

        assert query_measurement.body_weight == 127
        assert (
            query_measurement.measurement_time.date()
            == (datetime.utcnow() + timedelta(days=-10)).date()
        )

    def test_change_measurement_system(self):
        measurements = measurement_interface.get_all_measurement_by_user(1)

        measurement_interface.change_measurement_system(1, 1)
        measurement_interface.change_measurement_system(1, 1)

        new_measurements = measurement_interface.get_all_measurement_by_user(1)

        for m in measurements:
            new_measurement = [n for n in new_measurements if n.id == m.id]

            assert len(new_measurement) == 1
            new_measurement = new_measurement[0]

            assert new_measurement.id == m.id
            assert new_measurement.user_id == m.user_id
            assert (
                new_measurement.height == m.height
                or math.ceil(new_measurement.height) == m.height
                or math.floor(new_measurement.height) == m.height
            )
            assert (
                new_measurement.body_weight == m.body_weight
                or math.ceil(new_measurement.body_weight) == m.body_weight
                or math.floor(new_measurement.body_weight) == m.body_weight
            )


class TestRoutine:
    def test_add_routine(self):
        user_id = 1
        routine_name = "TEST ROUTINE"
        num_days = 4
        routine_interface.add_routine(user_id, routine_name, num_days)

        session = routine_interface.Session()
        routine = session.query(syfit.Routine).filter(syfit.Routine.user_id == 1).all()

        assert len(routine) == 1

        routine = routine[0]

        assert routine.user_id == user_id
        assert routine.routine_name == routine_name
        assert routine.num_days == num_days
        assert routine.is_current == True

    def test_get_all_user_routines(self):
        routine = routine_interface.get_all_user_routines(1)

        assert len(routine) == 1
        routine = routine[0]

        assert isinstance(routine, syfit.Routine)
        assert routine.user_id == 1
        assert routine.routine_name == "TEST ROUTINE"
        assert routine.num_days == 4

    def test_get_routine_by_id(self):
        routine = routine_interface.get_routine_by_id(1)

        assert isinstance(routine, syfit.Routine)
        assert routine.user_id == 1
        assert routine.routine_name == "TEST ROUTINE"
        assert routine.num_days == 4

    def test_edit_routine(self):
        routine_interface.edit_routine(
            1, routine_name="CHANGED ROUTINE NAME", num_days=5
        )

        routine = routine_interface.get_routine_by_id(1)

        assert routine.user_id == 1
        assert routine.routine_name == "CHANGED ROUTINE NAME"
        assert routine.num_days == 5

    def test_make_routine_not_current(self):
        assert routine_interface.get_routine_by_id(1).is_current == True

        routine_interface.make_routine_not_current(1)

        routine = routine_interface.get_routine_by_id(1)

        assert routine.is_current == False

    def test_make_routine_current(self):
        routine_interface.add_routine(1, "NEW ROUTINE", 3)

        routine_interface.make_routine_current(1)

        routine = routine_interface.get_routine_by_id(1)
        new_routine = routine_interface.get_routine_by_id(2)

        assert routine.is_current == True
        assert new_routine.is_current == False


class TestRoutineDay:
    def test_add_routine_day(self):
        routine_day_interface.add_routine_day(1, "LEGS & GLUTES", "mon")
        routine_day_interface.add_routine_day(1, "CHEST & ABS", "tue")
        routine_day_interface.add_routine_day(1, "BACK & ARMS", "wed")
        routine_day_interface.add_routine_day(1, "CARDIO", "thu")
        routine_day_interface.add_routine_day(1, "LEGS & GLUTES", "fri")

        session = routine_day_interface.Session()

        days = (
            session.query(syfit.RoutineDay)
            .filter(syfit.RoutineDay.routine_id == 1)
            .all()
        )

        assert len(days) == 5

        test_legs = [d for d in days if d.routine_day_name == "LEGS & GLUTES"]
        assert len(test_legs) == 2

        test_cardio = [d for d in days if d.routine_day_name == "CARDIO"]
        assert len(test_cardio) == 1

        test_chest = [d for d in days if d.routine_day_name == "CHEST & ABS"]
        assert len(test_chest) == 1

        test_back = [d for d in days if d.routine_day_name == "BACK & ARMS"]
        assert len(test_back) == 1

    def test_get_routine_day_by_id(self):
        day = routine_day_interface.get_routine_day_by_id(1)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & GLUTES"
        assert day.day_of_week == "mon"
        assert day.day_idx == 0

    def test_get_all_days_by_routine_id(self):
        days = routine_day_interface.get_days_by_routine_id(1)

        assert len(days) == 5

        test_legs = [d for d in days if d.routine_day_name == "LEGS & GLUTES"]
        assert len(test_legs) == 2

        test_cardio = [d for d in days if d.routine_day_name == "CARDIO"]
        assert len(test_cardio) == 1

        test_chest = [d for d in days if d.routine_day_name == "CHEST & ABS"]
        assert len(test_chest) == 1

        test_back = [d for d in days if d.routine_day_name == "BACK & ARMS"]
        assert len(test_back) == 1

    def test_get_routine_day_by_idx(self):
        day = routine_day_interface.get_routine_day_by_idx(1, 0)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & GLUTES"
        assert day.day_of_week == "mon"
        assert day.day_idx == 0

    def test_edit_routine_day(self):
        routine_day_interface.edit_routine_day(
            1, routine_day_name="LEGS & BUTT", day_of_week="sun"
        )

        day = routine_day_interface.get_routine_day_by_id(1)

        assert day.id == 1
        assert day.routine_id == 1
        assert day.routine_day_name == "LEGS & BUTT"
        assert day.day_of_week == "sun"
        assert day.day_idx == 0


class TestExercise:
    def test_add_exercise(self):
        exercise_name = "bodyweight squat"
        reference_link = "www.test.com"
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        rep_type = "reps"

        exercise_interface.add_exercise(
            exercise_name, reference_link, body_part, secondary_body_part, rep_type
        )

        session = exercise_interface.Session()
        exercises = session.query(syfit.Exercise).all()

        assert len(exercises) == 1
        query_exercise = exercises[0]

        assert exercise_name == query_exercise.exercise_name
        assert reference_link == query_exercise.reference_link
        assert body_part == query_exercise.body_part
        assert secondary_body_part == query_exercise.secondary_body_part
        assert rep_type == query_exercise.rep_type

    def test_add_duplicate_exercise(self):
        exercise_name = "bodyweight squat"
        reference_link = "www.test.com"
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        rep_type = "reps"

        duplicate_exercise = exercise_interface.add_exercise(
            exercise_name, reference_link, body_part, secondary_body_part, rep_type
        )

        session = exercise_interface.Session()
        exercises = (
            session.query(syfit.Exercise)
            .filter(syfit.Exercise.exercise_name == exercise_name)
            .all()
        )

        assert len(exercises) == 1
        assert isinstance(duplicate_exercise, str)

    def test_get_exercise_by_id(self):
        exercise = exercise_interface.get_exercise_by_id(1)
        session = exercise_interface.Session()
        query_exercise = (
            session.query(syfit.Exercise).filter(syfit.Exercise.id == 1).first()
        )

        assert exercise.id == query_exercise.id
        assert exercise.exercise_name == query_exercise.exercise_name
        assert exercise.reference_link == query_exercise.reference_link
        assert exercise.body_part == query_exercise.body_part
        assert exercise.secondary_body_part == query_exercise.secondary_body_part
        assert exercise.rep_type == query_exercise.rep_type

    def test_get_exercise_by_name(self):
        exercise = exercise_interface.get_exercise_by_name("bodyweight squat")
        session = exercise_interface.Session()
        query_exercise = (
            session.query(syfit.Exercise)
            .filter(syfit.Exercise.exercise_name == "bodyweight squat")
            .first()
        )

        assert exercise.id == query_exercise.id
        assert exercise.exercise_name == query_exercise.exercise_name
        assert exercise.reference_link == query_exercise.reference_link
        assert exercise.body_part == query_exercise.body_part
        assert exercise.secondary_body_part == query_exercise.secondary_body_part
        assert exercise.rep_type == query_exercise.rep_type

    def test_get_exercises_by_body_part(self):
        body_part = "upper_legs"
        secondary_body_part = "lower_legs"
        ref_link = "test.com"
        exercise_interface.add_exercise(
            "barbell squat", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "bulgarian split squat", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "box squat", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "bodyweight lunge", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "leg press", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "sumo squat", ref_link, body_part, secondary_body_part, "reps"
        )

        body_part = "chest"
        secondary_body_part = "shoulders"
        exercise_interface.add_exercise(
            "barbell bench press", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "incline bench press", ref_link, body_part, secondary_body_part, "reps"
        )
        exercise_interface.add_exercise(
            "dumbbell bench press", ref_link, body_part, secondary_body_part, "reps"
        )

        body_part = "shoulders"
        secondary_body_part = "biceps"
        exercise_interface.add_exercise(
            "dumbbell arnold press", ref_link, body_part, secondary_body_part, "reps"
        )
        secondary_body_part = "forearms"
        exercise_interface.add_exercise(
            "dumbbell lateral raise", ref_link, body_part, secondary_body_part, "reps"
        )

        leg_exercises = exercise_interface.get_exercises_by_body_part("upper_legs")
        chest_exercises = exercise_interface.get_exercises_by_body_part("chest")
        shoulder_exercises = exercise_interface.get_exercises_by_body_part("shoulders")
        bicep_exercises = exercise_interface.get_exercises_by_body_part("biceps")
        forearm_exercises = exercise_interface.get_exercises_by_body_part("forearms")

        assert len(leg_exercises) == 7
        assert len(chest_exercises) == 3
        assert len(shoulder_exercises) == 5
        assert len(bicep_exercises) == 1
        assert len(forearm_exercises) == 1

    def test_get_exercises_match_string(self):
        squats = exercise_interface.get_exercises_match_string("squat")
        press = exercise_interface.get_exercises_match_string("press")
        dumbbell = exercise_interface.get_exercises_match_string("dumbbell")

        assert len(squats) == 5
        assert len(press) == 5
        assert len(dumbbell) == 3

    def test_edit_exercise(self):
        name = "edit me"
        ref_link = "delete.com"
        body_part = "forearms"
        secondary_body_part = None
        rep_type = "reps"

        old_exercise = exercise_interface.add_exercise(
            name, ref_link, body_part, secondary_body_part, rep_type
        )

        new_name = "delete me"
        exercise_interface.edit_exercise(old_exercise.id, exercise_name=new_name)

        exercise = exercise_interface.get_exercise_by_name(new_name)

        assert exercise_interface.get_exercise_by_name(name) is None
        assert exercise is not None
        assert exercise.id == old_exercise.id
        assert exercise.reference_link == ref_link
        assert exercise.body_part == body_part
        assert exercise.secondary_body_part == secondary_body_part
        assert exercise.rep_type == rep_type

    def test_get_user_created_exercise(self):
        name = "user created exercise"
        ref_link = "used.com"
        body_part = "core"
        secondary_body_part = "back"
        exercise_interface.add_exercise(
            name, ref_link, body_part, secondary_body_part, "reps", 1
        )

        exercises = exercise_interface.get_user_created_exercises(1)

        assert len(exercises) == 1


class TestRoutineExercise:

    def test_add_routine_exercise(self):
        e = routine_exercise_interface.add_routine_exercise(day_id=1, exercise_id=1)

        assert e.exercise_idx == 0

        e = routine_exercise_interface.add_routine_exercise(day_id=1, exercise_id=2)

        assert e.exercise_idx == 1

        e = routine_exercise_interface.add_routine_exercise(
            day_id=1, exercise_id=3, num_sets=4, default_reps=12
        )

        assert e.exercise_idx == 2

        e = routine_exercise_interface.add_routine_exercise(
            day_id=1, exercise_id=4, default_time=60
        )

        assert e.exercise_idx == 3

        session = routine_exercise_interface.Session()
        routine_exercises = (
            session.query(syfit.RoutineExercise)
            .filter(syfit.RoutineExercise.day_id == 1)
            .all()
        )
        session.close()

        assert len(routine_exercises) == 4

    def test_get_exercises_by_routine_day(self):
        exercises = routine_exercise_interface.get_exercises_by_routine_day_id(1)
        ex_idxs = [e.exercise_idx for e in exercises]

        assert len(exercises) == 4
        assert list(set(ex_idxs)) == ex_idxs

    def test_get_routine_exercise_by_id(self):
        exercise = routine_exercise_interface.get_routine_exercise_by_id(3)

        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 4
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None

    def test_get_routine_exercise_by_idx(self):
        exercise = routine_exercise_interface.get_routine_exercise_by_idx(1, 2)
        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 4
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None

    def test_edit_routine_exercise(self):
        routine_exercise_interface.edit_routine_exercise(3, num_sets=5)

        exercise = routine_exercise_interface.get_routine_exercise_by_id(3)
        assert exercise.id == 3
        assert exercise.day_id == 1
        assert exercise.exercise_id == 3
        assert exercise.exercise_idx == 2
        assert exercise.num_sets == 5
        assert exercise.default_reps == 12
        assert exercise.default_time is None
        assert exercise.warmup_schema is None


class TestExerciseLog:
    def test_add_exercise_log(self):
        exercise_log_interface.add_log(1, datetime.utcnow(), 10)
        exercise_log_interface.add_log(1, datetime.utcnow(), 10)
        exercise_log_interface.add_log(1, datetime.utcnow(), 10)

        session = exercise_log_interface.Session()
        logs = (
            session.query(syfit.ExerciseLog)
            .filter(syfit.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == 3

    def test_get_exercise_logs_by_routine_exercise_id(self):
        logs = exercise_log_interface.get_exercise_logs_by_routine_exercise_id(1)

        session = exercise_log_interface.Session()

        query_logs = (
            session.query(syfit.ExerciseLog)
            .filter(syfit.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == len(query_logs)

    def test_get_exercise_log_by_id(self):
        log = exercise_log_interface.get_exercise_log_by_id(1)

        session = exercise_log_interface.Session()

        query_log = (
            session.query(syfit.ExerciseLog).filter(syfit.ExerciseLog.id == 1).first()
        )

        assert log.id == query_log.id
        assert log.routine_exercise_id == query_log.routine_exercise_id
        assert log.time_stamp == query_log.time_stamp
        assert log.set_idx == query_log.set_idx
        assert log.num_reps == query_log.num_reps
        assert log.time_duration == query_log.time_duration

    def test_get_exercise_log_by_set(self):
        log = exercise_log_interface.get_exercise_log_by_set(1, 1)

        session = exercise_interface.Session()
        query_log = (
            session.query(syfit.ExerciseLog)
            .filter(
                and_(
                    syfit.ExerciseLog.routine_exercise_id == 1,
                    syfit.ExerciseLog.set_idx == 1,
                )
            )
            .first()
        )

        assert log.id == query_log.id
        assert log.routine_exercise_id == query_log.routine_exercise_id
        assert log.time_stamp == query_log.time_stamp
        assert log.set_idx == query_log.set_idx
        assert log.num_reps == query_log.num_reps
        assert log.time_duration == query_log.time_duration

    def test_edit_exercise_log(self):
        exercise_log_interface.edit_exercise_log(1, num_reps=9)

        log = exercise_log_interface.get_exercise_log_by_id(1)

        assert log.num_reps == 9

    def test_get_exercise_log_by_routine_exercise(self):
        logs = exercise_log_interface.get_exercise_logs_by_routine_exercise(1)
        for l in logs:
            assert l.routine_exercise_id == 1


class TestDelete:
    __test__ = False

    def test_delete_user(self):
        delete_user = user_interface.add_user(
            "delete", "me", "delete_me", datetime.today().date(), "metric"
        )

        assert user_interface.get_user_by_username("delete_me") is not None

        user_interface.delete_user(delete_user.id)

        assert user_interface.get_user_by_username("delete_me") is None

    def test_delete_measurements(self):
        measurement_interface.delete_measurement(7)

        session = measurement_interface.Session()

        query_measurements = (
            session.query(syfit.Measurement).filter(syfit.Measurement.id == 7).all()
        )

        assert len(query_measurements) == 0

    def test_delete_all_measurements_by_user(self):
        user_id = 1
        measurement_interface.delete_all_measurements_by_user(user_id)

        session = measurement_interface.Session()
        measurements = (
            session.query(syfit.Measurement)
            .filter(syfit.Measurement.user_id == user_id)
            .all()
        )

        assert len(measurements) == 0

    def test_delete_routine(self):
        routine_interface.delete_routine(2)

        session = routine_interface.Session()

        routine = session.query(syfit.Routine).filter(syfit.Routine.id == 2).all()

        assert len(routine) == 0

    def test_delete_day_by_id(self):
        routine_day_interface.delete_day_by_id(4)

        days = routine_day_interface.get_days_by_routine_id(1)

        assert len(days) == 4

        for n, d in enumerate(days):
            assert n == d.day_idx

    def test_delete_days_by_routine_id(self):
        routine_day_interface.delete_days_by_routine_id(1)

        session = routine_day_interface.Session()

        days = (
            session.query(syfit.RoutineDay)
            .filter(syfit.RoutineDay.routine_id == 1)
            .all()
        )

        assert len(days) == 0

        routine = session.query(syfit.Routine).filter(syfit.Routine.id == 1).all()

        assert len(routine) == 0

    def test_delete_exercise(self):
        exercise_id = exercise_interface.get_exercise_by_name("delete me").id

        exercise_interface.delete_exercise(exercise_id)

        session = exercise_interface.Session()
        exercise = (
            session.query(syfit.Exercise)
            .filter(syfit.Exercise.id == exercise_id)
            .first()
        )

        assert exercise is None

        exercise = (
            session.query(syfit.Exercise)
            .filter(syfit.Exercise.exercise_name == "delete me")
            .first()
        )

        assert exercise is None

    def test_delete_exercise_by_id(self):
        routine_exercise_interface.delete_exercise_by_id(3)
        exercises = routine_exercise_interface.get_exercises_by_routine_day_id(1)

        assert len(exercises) == 3
        for n, d in enumerate(exercises):
            assert n == d.exercise_idx

    def test_delete_exercises_by_day_id(self):
        routine_exercise_interface.delete_exercises_by_day_id(1)

        session = routine_day_interface.Session()

        exercises = (
            session.query(syfit.RoutineExercise)
            .filter(syfit.RoutineExercise.day_id == 1)
            .all()
        )

        assert len(exercises) == 0

        routine_day = (
            session.query(syfit.RoutineDay).filter(syfit.RoutineDay.id == 1).all()
        )

        assert len(routine_day) == 0

    def test_delete_exercises_by_routine_exercise_id(self):
        exercise_log_interface.delete_exercises_by_routine_exercise_id(1)

        session = exercise_log_interface.Session()

        logs = (
            session.query(syfit.ExerciseLog)
            .filter(syfit.ExerciseLog.routine_exercise_id == 1)
            .all()
        )

        assert len(logs) == 0

    def test_delete_exercise_log_by_id(self):
        num_logs_before = len(
            exercise_log_interface.get_exercise_logs_by_routine_exercise_id(1)
        )
        exercise_log_interface.delete_exercise_log_by_id(2)
        logs = exercise_log_interface.get_exercise_logs_by_routine_exercise_id(1)

        assert len(logs) == num_logs_before - 1

        for n, l in enumerate(logs):
            assert l.set_idx == n
