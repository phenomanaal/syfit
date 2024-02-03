import enum

class MeasurementSystemCheck(enum.Enum):
    imperial = "imperial"
    metric = "metric"


class DayOfWeekCheck(enum.Enum):
    mon = "mon"
    tue = "tue"
    wed = "wed"
    thu = "thu"
    fri = "fri"
    sat = "sat"
    sun = "sun"


class BodyPartCheck(enum.Enum):
    triceps = "triceps"
    chest = "chest"
    shoulders = "shoulders"
    biceps = "biceps"
    core = "core"
    back = "back"
    forearms = "forearms"
    upper_legs = "upper_legs"
    glutes = "glutes"
    cardio = "cardio"
    lower_legs = "lower_legs"
    other = "other"


class RepTypeCheck(enum.Enum):
    reps = "reps"
    time = "time"