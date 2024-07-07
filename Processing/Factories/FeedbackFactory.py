from typing import List
import json
from Models.DataModels.GetModels import *
from .factories import log, logError


class FeedbackFactory:
    @staticmethod
    def from_db_row(row) -> Feedback:
        try:
            log(f"Creating Feedback object from row: {row[1]}", "from_db_row")
            return Feedback(
                feedback_id=row[0],
                match_id=row[1],
                feedback_text=row[2],
                auth_uid=row[3]
            )
        except Exception as e:
            logError(f"Error creating Feedback object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(feedback: Feedback, with_id=True):
        try:
            log(f"Converting Feedback object to db row: {feedback.feedback_id}", "to_db_row")
            params = (feedback.match_id, feedback.feedback_text, feedback.auth_uid)
            if with_id:
                return (feedback.feedback_id,) + params
            return params
        except Exception as e:
            logError(f"Error converting Feedback object to db row: {feedback}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Feedback:
        try:
            log(f"Creating Feedback object from JSON: {data['feedback_id']}", "from_json")
            if isinstance(data, str):
                data = json.loads(data)
            return Feedback(
                feedback_id=data['feedback_id'],
                match_id=data['match_id'],
                feedback_text=data['feedback_text'],
                auth_uid=data['auth_uid']
            )
        except Exception as e:
            logError(f"Error creating Feedback object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(feedback: Feedback) -> dict:
        try:
            log(f"Converting Feedback object to JSON: {feedback.feedback_id}", "to_json")
            return {
                'feedback_id': feedback.feedback_id,
                'match_id': feedback.match_id,
                'feedback_text': feedback.feedback_text,
                'auth_uid': feedback.auth_uid
            }
        except Exception as e:
            logError(f"Error converting Feedback object to JSON: {feedback}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Feedback]:
        try:
            log(f"Creating list of Feedback objects from multiple rows: ", "from_db_rows")
            return [FeedbackFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Feedback objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(feedbacks: List[Feedback]) -> List[tuple]:
        try:
            log(f"Converting list of Feedback objects to db rows: ", "to_db_rows")
            return [FeedbackFactory.to_db_row(feedback) for feedback in feedbacks]
        except Exception as e:
            logError(f"Error converting list of Feedback objects to db rows. \n", e, "to_db_rows")
            raise

