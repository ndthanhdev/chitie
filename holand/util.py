import re
from datetime import datetime
from calendar import monthrange


class timerange:

    def __init__(self, time_from=None, time_to=None):
        self.time_from = time_from
        self.time_to = time_to

    @classmethod
    def from_str(cls, text: str):
        if text == 'this month':
            carrytime = datetime.today()
            month_range = monthrange(carrytime.year, carrytime.month)
            return cls(
                datetime(carrytime.year, carrytime.month, 1, 0, 0, 0),
                datetime(carrytime.year, carrytime.month, month_range[1], 23, 59, 59)
            )
        if text == 'today':
            carrytime = datetime.today()
            return cls(
                datetime(carrytime.year, carrytime.month, carrytime.day, 0, 0, 0),
                datetime(carrytime.year, carrytime.month, carrytime.day, 23, 59, 59)
            )
        if re.match(r"^\d{4}\-\d{1,2}$", text) is not None:
            year, month = map(lambda e: int(e), text.split("-"))
            month_range = monthrange(year, month)
            return cls(
                datetime(year, month, 1, 0, 0, 0),
                datetime(year, month, month_range[1], 23, 59, 59)
            )
        return cls()

    def is_valid(self):
        return self.time_from is not None and self.time_to is not None


def is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True
