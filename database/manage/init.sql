CREATE DATABASE IF NOT EXISTS syfit;

USE syfit;

CREATE TABLE IF NOT EXISTS user (
    id int NOT NULL AUTO_INCREMENT,
    first_name varchar(25) NOT NULL,
    last_name varchar(25) NOT NULL,
    username varchar(25) NOT NULL,
    DOB date NOT NULL,
    last_updated_username timestamp,
    CONSTRAINT user_pk PRIMARY KEY (id),
    UNIQUE(username)
);

CREATE TABLE IF NOT EXISTS measurement (
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    height float NOT NULL,
    height_units char(2) NOT NULL,
    body_weight float NOT NULL,
    weight_units char(3) NOT NULL,
    CONSTRAINT measurement_pk PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS routine (
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    num_days int,
    is_current boolean,
    CONSTRAINT routine_pk PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS routine_day (
    id int NOT NULL AUTO_INCREMENT,
    routine_id int NOT NULL,
    day_idx int,
    routine_day_name varchar(10),
    day_of_week varchar(3),
    CONSTRAINT routine_day_pk PRIMARY KEY (id),
    FOREIGN KEY (routine_id) REFERENCES routine(id)
);

CREATE TABLE IF NOT EXISTS exercise (
    id int NOT NULL AUTO_INCREMENT,
    exercise_name varchar(100) NOT NULL,
    reference_link varchar(255),
    body_part varchar(50),
    secondary_body_part varchar(50),
    rep_type varchar(4),
    CONSTRAINT exercise_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS routine_exercise (
    id int NOT NULL AUTO_INCREMENT,
    day_id int NOT NULL,
    exercise_id int NOT NULL,
    exercise_idx int,
    num_sets int,
    default_reps int,
    default_time float,
    CONSTRAINT routine_exercise_pk PRIMARY KEY (id),
    FOREIGN KEY (day_id) REFERENCES routine_day(id),
    FOREIGN KEY (exercise_id) REFERENCES exercise(id)
);

CREATE TABLE IF NOT EXISTS exercise_log (
    id int NOT NULL AUTO_INCREMENT,
    routine_exercise_id int NOT NULL,
    time_stamp timestamp NOT NULL,
    set_num int,
    num_reps int,
    time_duration float,
    CONSTRAINT exercise_log_pk PRIMARY KEY (id),
    FOREIGN KEY (routine_exercise_id) REFERENCES routine_exercise(id)
);