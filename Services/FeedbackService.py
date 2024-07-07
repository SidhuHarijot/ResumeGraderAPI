from Database.FeedbackDatabase import FeedbackDatabase
from .services import log, logError
from Models.RequestModels.Feedback import Create, Update, Get
from Models.DataModels.Feedback import Feedback


class FeedbackService:
    feedback: FeedbackDatabase = FeedbackDatabase()
    in_db: bool = False

    def __init__(self, feedback: Feedback = None, json_str: str = None, dict_obj: dict = None, db_row: Feedback = None):
        if dict_obj or json_str:
            feedback = Feedback.from_json(json_str)
        elif db_row:
            feedback = db_row
        if feedback:
            self.feedback = feedback
            self.check_in_db()
        else:
            raise ValueError("No valid arguments provided to FeedbackService constructor")
    
    def check_in_db(self):
        try:
            FeedbackDatabase.get_feedback(self.feedback.feedback_id)
            self.in_db = True
        except ValueError:
            self.in_db = False
            log(f"Feedback not found in database: {self.feedback.feedback_id}", "FeedbackService.check_in_db")
        return self.in_db
    
    def save_to_db(self):
        if not self.in_db:
            if not self.validate():
                raise ValueError("Invalid feedback data")
            FeedbackDatabase.create_feedback(self.feedback)
        else:
            self.update()
