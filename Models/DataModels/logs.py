from ServerLogging.serverLogger import Logger
import traceback

def log(message, func):
    Logger.logValidation(message, func)


def logError(message, e, func):
    message = message + "\n" + str(e) + "\n" + traceback.format_exc()
    Logger.logValidation(message, func, "ERROR")
