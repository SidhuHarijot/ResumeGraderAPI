from typing import List
from Models.DataModels.GetModels import *
from Processing.Factories.JobFactory import *
from .database import *


class JobDatabase:
    @staticmethod
    def create_job(job: Job):
        try:
            log(f"Creating job {job.title} at {job.company}", "JobDatabase.create_job")
            query = """
                INSERT INTO jobdescriptions (title, company, description, required_skills, application_deadline, location, salary, job_type, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING job_id
            """
            params = JobFactory.to_db_row(job, with_id=False)
            job_id = Database.execute_query(query, params, fetch=True)[0][0]
            log(f"Job {job.title} at {job.company} created successfully", "JobDatabase.create_job")
            return job_id
        except Exception as e:
            logError(e, "JobDatabase.create_job")
            raise

    @staticmethod
    def get_job(job_id: int) -> Job:
        try:
            log(f"Retrieving job {job_id}", "JobDatabase.get_job")
            query = "SELECT * FROM jobdescriptions WHERE job_id = %s"
            result = Database.execute_query(query, (job_id,), fetch=True)
            if result:
                job = JobFactory.from_db_row(result[0])
                log(f"Job {job_id} retrieved successfully", "JobDatabase.get_job")
                return job
            else:
                raise ValueError(f"Job {job_id} not found")
        except Exception as e:
            logError(e, "JobDatabase.get_job")
            raise

    @staticmethod
    def update_job(job: Job):
        try:
            log(f"Updating job {job.title} at {job.company}", "JobDatabase.update_job")
            query = """
                UPDATE jobdescriptions SET title = %s, company = %s, description = %s, required_skills = %s, application_deadline = %s, location = %s, salary = %s, job_type = %s, active = %s
                WHERE job_id = %s
            """
            params = JobFactory.to_db_row(job, False) + (job.job_id,)
            Database.execute_query(query, params)
            log(f"Job {job.title} at {job.company} updated successfully", "JobDatabase.update_job")
        except Exception as e:
            logError(e, "JobDatabase.update_job")
            raise

    @staticmethod
    def delete_job(job_id: int):
        try:
            log(f"Deleting job {job_id}", "JobDatabase.delete_job")
            query = "DELETE FROM jobdescriptions WHERE job_id = %s"
            Database.execute_query(query, (job_id,))
            log(f"Job {job_id} deleted successfully", "JobDatabase.delete_job")
        except Exception as e:
            logError(e, "JobDatabase.delete_job")
            raise

    @staticmethod
    def get_all_jobs() -> List[Job]:
        try:
            log("Retrieving all jobs", "JobDatabase.get_all_jobs")
            query = "SELECT * FROM jobdescriptions ORDER BY job_id ASC"
            results = Database.execute_query(query, fetch=True)
            jobs = JobFactory.from_db_rows(results)
            log("All jobs retrieved successfully", "JobDatabase.get_all_jobs")
            return jobs
        except Exception as e:
            logError(e, "JobDatabase.get_all_jobs")
            raise
    
    @staticmethod
    def find_jobs(params: dict) -> List[Job]:
        try:
            log(f"Finding job with params {params}", "JobDatabase.find_job")
            query = "SELECT * FROM jobdescriptions WHERE "
            query += " AND ".join([f"{key} = %s" for key in params.keys()])
            result = Database.execute_query(query, tuple(params.values()), fetch=True)
            if result:
                jobs = JobFactory.from_db_rows(result)
                log(f"{len(result)} jobs found.", "JobDatabase.find_job")
                return jobs
            else:
                raise ValueError(f"No job found")
        except Exception as e:
            logError(e, "JobDatabase.find_job")
            raise
