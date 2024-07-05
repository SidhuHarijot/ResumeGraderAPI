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


class ResumeService:
    @staticmethod
    def process_resume(file: UploadFile = None, resume_text: str = None) -> Resume:
        log("Processing resume", "ResumeService.process_resume")
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            resume_text = FileUtility.extract_text(temp_file_path)

        resume_json = OpenAIUtility.extract_resume_json(resume_text)
        resume_data = ResumeFactory.from_json(resume_json)
        log(f"Resume processed: {resume_data.uid}", "ResumeService.process_resume")
        return resume_data
    
class JobService:
    @staticmethod
    def process_job_description(file: UploadFile = None, job_description_text: str = None) -> Job:
        log("Processing job description", "JobService.process_job_description")
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            job_description_text = FileUtility.extract_text(temp_file_path)

        job_json = OpenAIUtility.extract_job_description_json(job_description_text)
        job_data = JobFactory.from_json(job_json)
        log(f"Job description processed: {job_data.job_id}", "JobService.process_job_description")
        return job_data


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
