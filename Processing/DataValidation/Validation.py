from ServerLogging.serverLogger import Logger
import traceback
from .EmailValidation import EmailValidation
from .PhoneValidation import PhoneValidation
from .DateValidation import DateValidation


def log(msg, func):
    Logger.logValidation(msg, func)


def logError(*args):
    try:
        message = args[0]
        if len(args) == 2:
            e = ValueError(args[0])
            func = args[1]
        else:    
            e = args[1]
            func = args[2]
        message = f"{message}\n{traceback.format_exception(None, e, e.__traceback__)}"
        Logger.logMain(message, func, "ERROR")
    except Exception as e:
        Logger.logMain(f"Error in logError: {e}", "main.logError", "ERROR")
        Logger.logMain(f"Original error: {message}", "main.logError", "ERROR")


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
