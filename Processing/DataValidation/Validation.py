from ServerLogging.serverLogger import Logger
import traceback
from .EmailValidation import EmailValidation
from .PhoneValidation import PhoneValidation
from .DateValidation import DateValidation


def log(msg, func):
    Logger.logValidation(msg, func)


def logError(msg, e, func):
    msg = f"{msg}. Exception: {''.join(traceback.format_exception(None, e, e.__traceback__))}"
    Logger.logValidation(msg, func, "ERROR")


class Validation:
    def validate_email(email: str) -> str:
        try:
            return EmailValidation.validate_email(email)
        except Exception as e:
            logError(f"Error validating email: {email}", e, "Validation.validate_email")
            return None

    def validate_phone_number(phone_number: str) -> str:
        try:
            return PhoneValidation.validate_phone_number(phone_number)
        except Exception as e:
            logError(f"Error validating phone number: {phone_number}", e, "Validation.validate_phone_number")
            return None
    
    def validate_date(date: str, min_date=None, max_date=None) -> str:
        try:
            return DateValidation.validate_date(date, min_date, max_date)
        except Exception as e:
            logError(f"Error validating date: {date}", e, "Validation.validate_date")
            return None
