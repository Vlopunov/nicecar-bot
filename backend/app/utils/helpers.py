from datetime import datetime, time
import zoneinfo

MINSK_TZ = zoneinfo.ZoneInfo("Europe/Minsk")


def now_minsk() -> datetime:
    return datetime.now(MINSK_TZ)


def format_price(price) -> str:
    p = float(price)
    if p == int(p):
        return f"{int(p)} BYN"
    return f"{p:.2f} BYN"


def format_date(d) -> str:
    months = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    return f"{d.day} {months[d.month]}"


def format_time(t: time) -> str:
    return t.strftime("%H:%M")


WORK_SCHEDULE = {
    0: (time(9, 0), time(19, 0)),  # Monday
    1: (time(9, 0), time(19, 0)),
    2: (time(9, 0), time(19, 0)),
    3: (time(9, 0), time(19, 0)),
    4: (time(9, 0), time(19, 0)),
    5: (time(9, 0), time(18, 0)),  # Saturday
    6: None,                        # Sunday — closed
}


def is_working_day(d) -> bool:
    return WORK_SCHEDULE.get(d.weekday()) is not None


def get_work_hours(d) -> tuple[time, time] | None:
    return WORK_SCHEDULE.get(d.weekday())
