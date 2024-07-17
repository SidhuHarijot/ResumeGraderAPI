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


def logError(msg, exception, func):
    msg = f"{msg}. Exception: {''.join(traceback.format_exception(None, exception, exception.__traceback__))}"
    Logger.logService(msg, func, "ERROR")





