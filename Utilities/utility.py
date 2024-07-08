from ServerLogging.serverLogger import Logger
import traceback


def log(msg, func):
    Logger.logService(msg, func)

def logError(msg, exception, func):
    msg = f"{msg}. Exception: {''.join(traceback.format_exception(None, exception, exception.__traceback__))}"
    Logger.logService(msg, func, "ERROR")
