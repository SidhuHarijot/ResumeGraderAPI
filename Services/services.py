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
    msg = f"{msg}. Exception: {traceback.format_exception(None, exception, exception.__traceback__)[0]}"
    Logger.logService(msg, func, "ERROR")





class GradingService:
    @staticmethod
    def grade_resumes_for_job(job_id: int):
        log(f"Grading resumes for job: {job_id}", "GradingService.grade_resumes_for_job")
        job = JobDatabase.get_job(job_id)
        job_description = job.description
        matches = MatchDatabase.get_matches_for_job(job_id)
        graded_matches = []
        for match in matches:
            resume = ResumeDatabase.get_resume(match.uid)
            resume_text = str(resume)
            grade = OpenAIUtility.grade_resume(resume_text, job_description, max_grade=100.0)
            match.grade = grade
            match.status = "GRADED"
            graded_matches.append(match)
        log(f"Resumes graded for job: {job_id}", "GradingService.grade_resumes_for_job")
        return graded_matches
