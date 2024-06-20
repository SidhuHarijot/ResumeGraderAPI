from ServerLogging.serverLogger import Logger
import traceback


def log(msg, func):
    Logger.logValidation(msg, func)


def logError(msg, e, func):
    msg = f"{msg}. Exception: {"".join(traceback.format_exception(None, e, e.__traceback__))}"
    Logger.logValidation(msg, func, "ERROR")
