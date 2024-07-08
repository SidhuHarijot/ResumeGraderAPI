from typing import List
from Models.DataModels.GetModels import *
from Processing.Factories.FeedbackFactory import *
from .database import Database, log, logError


class FeedbackDatabase:
    @staticmethod
    def create_feedback(feedback: Feedback):
        try:
            log(f"Creating feedback {feedback.feedback_id} for match {feedback.match_id}", "FeedbackDatabase.create_feedback")
            query = """
                INSERT INTO feedback (match_id, feedback_text, auth_uid)
                VALUES (%s, %s, %s) RETURNING feedback_id
            """
            params = FeedbackFactory.to_db_row(feedback, False)
            log(f"Creating feedback with params: {params}", "FeedbackDatabase.create_feedback")
            feedback_id = Database.execute_query(query, params, fetch=True)[0][0]
            log(f"Feedback {feedback.feedback_id} created successfully", "FeedbackDatabase.create_feedback")
            return feedback_id
        except Exception as e:
            logError(e, "FeedbackDatabase.create_feedback")
            raise

    @staticmethod
    def get_feedback(feedback_id: int) -> Feedback:
        try:
            log(f"Retrieving feedback {feedback_id}", "FeedbackDatabase.get_feedback")
            query = "SELECT * FROM feedback WHERE feedback_id = %s"
            result = Database.execute_query(query, (feedback_id,), fetch=True)
            if result:
                feedback = FeedbackFactory.from_db_row(result[0])
                log(f"Feedback {feedback_id} retrieved successfully", "FeedbackDatabase.get_feedback")
                return feedback
            else:
                raise ValueError(f"Feedback {feedback_id} not found")
        except Exception as e:
            logError(e, "FeedbackDatabase.get_feedback")
            raise

    @staticmethod
    def update_feedback(feedback: Feedback):
        try:
            log(f"Updating feedback {feedback.feedback_id} for match {feedback.match_id}", "FeedbackDatabase.update_feedback")
            query = """
                UPDATE feedback SET match_id = %s, feedback_text = %s, auth_uid = %s
                WHERE feedback_id = %s
            """
            params = FeedbackFactory.to_db_row(feedback, False) + (feedback.feedback_id,)
            Database.execute_query(query, params)
            log(f"Feedback {feedback.feedback_id} updated successfully", "FeedbackDatabase.update_feedback")
        except Exception as e:
            logError(e, "FeedbackDatabase.update_feedback")
            raise

    @staticmethod
    def delete_feedback(feedback_id: int):
        try:
            log(f"Deleting feedback {feedback_id}", "FeedbackDatabase.delete_feedback")
            query = "DELETE FROM feedback WHERE feedback_id = %s"
            Database.execute_query(query, (feedback_id,))
            log(f"Feedback {feedback_id} deleted successfully", "FeedbackDatabase.delete_feedback")
        except Exception as e:
            logError(e, "FeedbackDatabase.delete_feedback")
            raise
    
    def find(params):
        try:
            log(f"Finding feedback with params: {params}", "FeedbackDatabase.find")
            query = "SELECT * FROM feedback WHERE "
            query += " AND ".join([f"{key} = %s" for key in params.keys()])
            results = Database.execute_query(query, tuple(params.values()), fetch=True)
            feedbacks = FeedbackFactory.from_db_rows(results)
            log(f"Feedback found: {feedbacks}", "FeedbackDatabase.find")
            return feedbacks
        except Exception as e:
            logError(e, "FeedbackDatabase.find")
            raise

    @staticmethod
    def get_all_data():
        try:
            log("Retrieving all feedback data", "FeedbackDatabase.get_all_data")
            query = "SELECT * FROM feedback"
            results = Database.execute_query(query, fetch=True)
            feedbacks = FeedbackFactory.from_db_rows(results)
            log("All feedback data retrieved successfully", "FeedbackDatabase.get_all_data")
            return feedbacks
        except Exception as e:
            logError(e, "FeedbackDatabase.get_all_data")
            raise
