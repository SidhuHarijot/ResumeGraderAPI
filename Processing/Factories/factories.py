from Models.datamodels import *
from ServerLogging.serverLogger import Logger
from typing import List
import json
import traceback


def log(message, func):
    Logger.logFactories(message, func)

def logError(log, e: Exception, func):
    error_message = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    message = f"{log}: {str(e)}\n{error_message}"
    Logger.logFactories(message, func, "ERROR")










