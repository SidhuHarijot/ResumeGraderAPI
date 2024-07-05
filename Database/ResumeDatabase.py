from typing import List
from Models.DataModels.GetModels import *
from Processing.Factories.ResumeFactory import *
from .database import *

class ResumeDatabase:
    @staticmethod
    def create_resume(resume: Resume):
        try:
            log(f"Creating resume for user {resume.uid}", "ResumeDatabase.create_resume")
            query = """
                INSERT INTO resumes (uid, skills, experience, education)
                VALUES (%s, %s, %s, %s)
            """
            params = ResumeFactory.to_db_row(resume)
            Database.execute_query(query, params)
            log(f"Resume for user {resume.uid} created successfully", "ResumeDatabase.create_resume")
        except Exception as e:
            logError(e, "ResumeDatabase.create_resume")
            raise

    @staticmethod
    def get_resume(uid: str) -> Resume:
        try:
            log(f"Retrieving resume for user {uid}", "ResumeDatabase.get_resume")
            query = "SELECT * FROM resumes WHERE uid = %s"
            result = Database.execute_query(query, (uid,), fetch=True)
            if result:
                resume = ResumeFactory.from_db_row(result[0])
                log(f"Resume for user {uid} retrieved successfully", "ResumeDatabase.get_resume")
                return resume
            else:
                raise ValueError(f"Resume for user {uid} not found")
        except Exception as e:
            logError(e, "ResumeDatabase.get_resume")
            raise

    @staticmethod
    def update_resume(resume: Resume):
        try:
            log(f"Updating resume for user {resume.uid}", "ResumeDatabase.update_resume")
            query = """
                UPDATE resumes SET skills = %s, experience = %s, education = %s
                WHERE uid = %s
            """
            params = ResumeFactory.to_db_row(resume) + (resume.uid,)
            Database.execute_query(query, params)
            log(f"Resume for user {resume.uid} updated successfully", "ResumeDatabase.update_resume")
        except Exception as e:
            logError(e, "ResumeDatabase.update_resume")
            raise

    @staticmethod
    def delete_resume(uid: str):
        try:
            log(f"Deleting resume for user {uid}", "ResumeDatabase.delete_resume")
            query = "DELETE FROM resumes WHERE uid = %s"
            Database.execute_query(query, (uid,))
            log(f"Resume for user {uid} deleted successfully", "ResumeDatabase.delete_resume")
        except Exception as e:
            logError(e, "ResumeDatabase.delete_resume")
            raise

    @staticmethod
    def get_all_resumes() -> List[Resume]:
        try:
            log("Retrieving all resumes", "ResumeDatabase.get_all_resumes")
            query = "SELECT * FROM resumes"
            results = Database.execute_query(query, fetch=True)
            resumes = ResumeFactory.from_db_rows(results)
            log("All resumes retrieved successfully", "ResumeDatabase.get_all_resumes")
            return resumes
        except Exception as e:
            logError(e, "ResumeDatabase.get_all_resumes")
            raise
