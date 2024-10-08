from Utilities.GetUtilities import OpenAIUtility, FileUtility
from Models.DataModels.GetModels import Resume, Job, Match
import json
from fastapi import UploadFile
from Processing.Factories.GetFactories import ResumeFactory, JobFactory
from Database.GetDatabases import JobDatabase, ResumeDatabase, MatchDatabase
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
        Logger.logService(message, func, "ERROR")
    except Exception as e:
        Logger.logService(f"Error in logError: {e}", "main.logError", "ERROR")
        Logger.logService(f"Original error: {message}", "main.logError", "ERROR")





