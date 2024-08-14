from ServerLogging.serverLogger import Logger
import traceback


def log(msg, func):
    Logger.logService(msg, func)

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
        Logger.log("Utility", message, func, "ERROR")
    except Exception as e:
        Logger.log("Utility", f"Error in logError: {e}", "main.logError", "ERROR")
        Logger.log("Utility", f"Original error: {message}", "main.logError", "ERROR")
