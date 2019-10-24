import datetime

from enumchoicefield import ChoiceEnum


class WeatherType(ChoiceEnum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    SNOWY = "snowy"
    RAINY = "rainy"
    WINDY = "windy"


class TemperatureType(ChoiceEnum):
    COLD = "cold"
    COOL = "cool"
    MILD = "mild"
    WARM = "warm"
    HOT = "hot"


class LengthOfTripType(ChoiceEnum):
    MANY_HRS = "many hours"
    FEW_HRS = "a few hours"
    ONE_HR = "up to an hour"


class CrowdednessType(ChoiceEnum):
    EMPTY = "empty"
    MEDIUM_CROWDED = "medium crowded"
    VERY_CROWDED = "very crowded"


class TimeOfDayType(ChoiceEnum):
    EARLY_MORNING = "early morning"
    LATE_MORNING = "late morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


def get_time_of_day(time):
    if datetime.time(22, 0, 0) <= time <= datetime.time(23, 59, 59) or datetime.time(0, 0, 0) <= time < datetime.time(4, 0, 0):
        return TimeOfDayType.NIGHT
    elif datetime.time(18, 0, 0) <= time < datetime.time(22, 0, 0):
        return TimeOfDayType.EVENING
    elif datetime.time(13, 0, 0) <= time < datetime.time(18, 0, 0):
        return TimeOfDayType.AFTERNOON
    elif datetime.time(11, 0, 0) <= time < datetime.time(13, 0, 0):
        return TimeOfDayType.NOON
    elif datetime.time(8, 0, 0) <= time < datetime.time(11, 0, 0):
        return TimeOfDayType.LATE_MORNING
    elif datetime.time(4, 0, 0) <= time < datetime.time(8, 0, 0):
        return TimeOfDayType.EARLY_MORNING
