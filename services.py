from utility import OpenAIUtility, FileUtility
from datamodels import Resume, Job, Match
import json
from fastapi import UploadFile
from factories import ResumeFactory
from database import JobDatabase, ResumeDatabase, MatchDatabase

class ResumeService:
    @staticmethod
    def process_resume(file: UploadFile = None, resume_text: str = None) -> Resume:
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            resume_text = FileUtility.extract_text(temp_file_path)

        openai_util = OpenAIUtility()
        resume_json = openai_util.extract_resume_json(resume_text)
        resume_data = resume_json
        return ResumeFactory.from_json(resume_data)
    
class JobService:
    @staticmethod
    def process_job_description(file: UploadFile = None, job_description_text: str = None) -> Job:
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            job_description_text = FileUtility.extract_text(temp_file_path)

        openai_util = OpenAIUtility()
        job_json = openai_util.extract_job_description_json(job_description_text)
        job_data = json.loads(job_json)

        return Job(
            job_id=-1,
            title=job_data["Title"],
            company=job_data["Employer"],
            description=job_data["description"],
            required_skills=job_data["Must Haves"],
            application_deadline=job_data["application_deadline"],
            location=job_data["location"],
            salary=job_data["salary"],
            job_type=job_data["job_type"],
            active=job_data["active"]
        )


class GradingService:
    @staticmethod
    def grade_resumes_for_job(job_id: int):
        openai_utility = OpenAIUtility()
        job = JobDatabase.get_job(job_id)
        job_description = job.description
        matches = MatchDatabase.get_matches_for_job(job_id)
        graded_matches = []
        for match in matches:
            resume = ResumeDatabase.get_resume(match.uid)
            resume_text = resume.get_text()
            grade = openai_utility.grade_resume_for_job(resume_text, job_description)
            match.grade = grade
            graded_matches.append(match)
        return graded_matches
