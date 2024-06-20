from Models.DataModels import Date


class DateValidation:
    @staticmethod
    def check_date(date, min_date=None, max_date=None):
        if isinstance(date, str):
            try:
                date = Date.from_string(date)
            except ValueError:
                return None
        if not isinstance(date, Date):
            return None
        try:
            if min_date and max_date:
                min_date = Date.from_string(min_date) if isinstance(min_date, str) else min_date
                max_date = Date.from_string(max_date) if isinstance(max_date, str) else max_date
                if min_date > date or date > max_date:
                    return None
            return date
        except ValueError:
            return None