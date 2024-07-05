from typing import List
from Models.DataModels.GetModels import *
from Processing.Factories.MatchFactory import *
from .database import *

class MatchDatabase:
    @staticmethod
    def create_match(match: Match):
        try:
            log(f"Creating match {match.match_id} for user {match.uid} and job {match.job_id}", "MatchDatabase.create_match")
            query = """
                INSERT INTO matches (uid, job_id, status, status_code, grade, selected_skills)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = MatchFactory.to_db_row(match, False)
            Database.execute_query(query, params)
            log(f"Match {match.match_id} created successfully", "MatchDatabase.create_match")
        except Exception as e:
            logError(e, "MatchDatabase.create_match")
            raise

    @staticmethod
    def get_match(match_id: int) -> Match:
        try:
            log(f"Retrieving match {match_id}", "MatchDatabase.get_match")
            query = "SELECT * FROM matches WHERE match_id = %s"
            result = Database.execute_query(query, (match_id,), fetch=True)
            if result:
                match = MatchFactory.from_db_row(result[0])
                log(f"Match {match_id} retrieved successfully", "MatchDatabase.get_match")
                return match
            else:
                raise ValueError(f"Match {match_id} not found")
        except Exception as e:
            logError(e, "MatchDatabase.get_match")
            raise

    @staticmethod
    def update_match(match: Match):
        try:
            log(f"Updating match {match.match_id} for user {match.uid} and job {match.job_id}", "MatchDatabase.update_match")
            query = """
                UPDATE matches SET uid = %s, job_id = %s, status = %s, status_code = %s, grade = %s, selected_skills = %s
                WHERE match_id = %s
            """
            params = MatchFactory.to_db_row(match) + (match.match_id,)
            Database.execute_query(query, params)
            log(f"Match {match.match_id} updated successfully", "MatchDatabase.update_match")
        except Exception as e:
            logError(e, "MatchDatabase.update_match")
            raise

    @staticmethod
    def delete_match(match_id: int):
        try:
            log(f"Deleting match {match_id}", "MatchDatabase.delete_match")
            query = "DELETE FROM matches WHERE match_id = %s"
            Database.execute_query(query, (match_id,))
            log(f"Match {match_id} deleted successfully", "MatchDatabase.delete_match")
        except Exception as e:
            logError(e, "MatchDatabase.delete_match")
            raise

    @staticmethod
    def get_all_matches() -> List[Match]:
        try:
            log("Retrieving all matches", "MatchDatabase.get_all_matches")
            query = "SELECT * FROM matches"
            results = Database.execute_query(query, fetch=True)
            matches = MatchFactory.from_db_rows(results)
            log("All matches retrieved successfully", "MatchDatabase.get_all_matches")
            return matches
        except Exception as e:
            logError(e, "MatchDatabase.get_all_matches")
            raise
    
    def get_matches_for_job(job_id: int) -> List[Match]:
        try:
            log(f"Retrieving all matches for job {job_id}", "MatchDatabase.get_matches_for_job")
            query = "SELECT * FROM matches WHERE job_id = %s"
            results = Database.execute_query(query, (job_id,), fetch=True)
            matches = MatchFactory.from_db_rows(results)
            log(f"All matches for job {job_id} retrieved successfully", "MatchDatabase.get_matches_for_job")
            return matches
        except Exception as e:
            logError(e, "MatchDatabase.get_matches_for_job")
            raise
