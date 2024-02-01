CREATE DATABASE {};

DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    id SERIAL PRIMARY KEY,
    first_name varchar(25) NOT NULL,
    last_name varchar(25) NOT NULL,
    username varchar(25) NOT NULL UNIQUE,
    DOB date NOT NULL,
    last_updated_username timestamp,
    measurement_system varchar(10) CHECK (measurement_system IN ('imperial', 'metric'))
);

DROP TABLE IF EXISTS measurement;
CREATE TABLE measurement (
    id SERIAL PRIMARY KEY,
    measurement_time timestamp NOT NULL,
    user_id int NOT NULL REFERENCES app_user(id),
    height float,
    body_weight float
);

DROP TABLE IF EXISTS routine;
CREATE TABLE routine (
    id SERIAL PRIMARY KEY,
    routine_name varchar(20) NOT NULL,
    user_id int NOT NULL REFERENCES app_user(id),
    num_days int,
    is_current boolean
);

DROP TABLE IF EXISTS routine_day;
CREATE TABLE routine_day (
    id SERIAL PRIMARY KEY,
    routine_id int NOT NULL REFERENCES routine(id),
    day_idx int,
    routine_day_name varchar(20),
    day_of_week varchar(3)
);

DROP TABLE IF EXISTS exercise;
CREATE TABLE exercise (
    id SERIAL PRIMARY KEY,
    exercise_name varchar(100) NOT NULL,
    reference_link varchar(255),
    body_part varchar(50),
    secondary_body_part varchar(50),
    rep_type varchar(4)
);

DROP TABLE IF EXISTS routine_exercise;
CREATE TABLE routine_exercise (
    id SERIAL PRIMARY KEY,
    day_id int NOT NULL REFERENCES routine_day(id),
    exercise_id int NOT NULL REFERENCES exercise(id),
    exercise_idx int,
    num_sets int,
    default_reps int,
    default_time float
);

DROP TABLE IF EXISTS exercise_log;
CREATE TABLE exercise_log (
    id SERIAL PRIMARY KEY,
    routine_exercise_id int NOT NULL REFERENCES routine_exercise(id),
    time_stamp timestamp NOT NULL,
    set_num int,
    num_reps int,
    time_duration float
);