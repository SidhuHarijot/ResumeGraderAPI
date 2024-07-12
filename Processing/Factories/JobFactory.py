from typing import List
import json
from Models.DataModels.GetModels import Job, Date
from .factories import *
from typing import Dict


class JobFactory:
    @staticmethod
    def from_db_row(row) -> Job:
        try:
            log(f"Creating Job object from row: {row[1]}", "from_db_row")
            return Job(
                job_id=row[0],
                title=row[1],
                company=row[2],
                description=row[3],
                required_skills=row[4],
                application_deadline=Date.create(row[5]),
                location=row[6],
                salary=row[7],
                job_type=row[8],
                active=row[9]
            )
        except Exception as e:
            logError(f"Error creating Job object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(job: Job, with_id=True):
        try:
            log(f"Converting Job object to db row: {job.title} at {job.company}", "to_db_row")
            deadline_str = str(job.application_deadline)
            params = (
                job.title,
                job.company,
                job.description,
                job.required_skills,
                deadline_str,
                job.location,
                job.salary,
                job.job_type,
                job.active
            )
            if not with_id or job.job_id == -1:
                return params
            return (job.job_id,) + params
        except Exception as e:
            logError(f"Error converting Job object to db row: {job} at {job}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Job:
        try:
            log(f"Creating Job object from JSON: {data['title']} at {data['company']}", "from_json")
            if isinstance(data, str):
                data = json.loads(data)
            job = Job.generate_default()
            if 'job_id' in data:
                job.job_id = data['job_id']
            if 'title' in data:
                job.title = data['title']
            if 'company' in data:
                job.company = data['company']
            if 'description' in data:
                job.description = data['description']
            if 'required_skills' in data:
                job.required_skills = data['required_skills']
            if 'application_deadline' in data:
                job.application_deadline = Date.create(data['application_deadline'])
            if 'location' in data:
                job.location = data['location']
            if 'salary' in data:
                job.salary = data['salary']
            if 'job_type' in data:
                job.job_type = data['job_type']
            if 'active' in data:
                job.active = data['active']
            return job
        except Exception as e:
            logError(f"Error creating Job object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(job: Job) -> dict:
        try:
            log(f"Converting Job object to JSON: {job.title} at {job.company}", "to_json")
            return {
                'job_id': job.job_id,
                'title': job.title,
                'company': job.company,
                'description': job.description,
                'required_skills': job.required_skills,
                'application_deadline': str(job.application_deadline),
                'location': job.location,
                'salary': job.salary,
                'job_type': job.job_type,
                'active': job.active
            }
        except Exception as e:
            logError(f"Error converting Job object to JSON: {job}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Job]:
        try:
            log(f"Creating list of Job objects from multiple rows: ", "from_db_rows")
            return [JobFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Job objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(jobs: List[Job]) -> List[tuple]:
        try:
            log(f"Converting list of Job objects to db rows: ", "to_db_rows")
            return [JobFactory.to_db_row(job) for job in jobs]
        except Exception as e:
            logError(f"Error converting list of Job objects to db rows. \n", e, "to_db_rows")
            raise
    
    @staticmethod
    def to_text(job: Job, exclude:List[str]=[]) -> str:
        try:
            log(f"Converting Job object to text: {job.title} at {job.company}", "to_text")
            job_dict = JobFactory.to_json(job)
            return_string = ""
            for key in exclude:
                del job_dict[key]
            for key, value in job_dict.items():
                return_string += f"{key}: {value}||\n"
            return return_string
        except Exception as e:
            logError(f"Error converting Job object to text: {job}. \n", e, "to_text")
            raise
