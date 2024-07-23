from Database.FeedbackDatabase import FeedbackDatabase
from Database.database import Database
from .services import log, logError
from Models.RequestModels.Feedback import Create, Update, Get
from Models.RequestModels.Matches import Update as MatchUpdate
from Models.DataModels.Feedback import Feedback
from Processing.Factories.FeedbackFactory import FeedbackFactory
from Processing.authorize import authorizeAdmin
from Errors.GetErrors import Errors as e
from Database.check import Exists
from .MatchService import MatchService


class FeedbackService:
    feedback: Feedback = None
    in_db: bool = False

    def __init__(self, feedback: Feedback = None, json_str: str = None, dict_obj: dict = None, db_row: Feedback = None):
        if dict_obj or json_str:
            feedback = FeedbackFactory.from_json(json_str)
        elif db_row:
            feedback = FeedbackFactory.from_db_row(db_row)
        if feedback:
            self.feedback = feedback
            self.check_in_db()
        else:
            raise ValueError("No valid arguments provided to FeedbackService constructor")
    
    def check_in_db(self):
        log(f"Checking if feedback is in database: {self.feedback.feedback_id}", "FeedbackService.check_in_db")
        if self.feedback.feedback_id == -1 or self.feedback.feedback_id is None:
            self.in_db = False
        else:
            return Exists.feedback(feedback_id=self.feedback.feedback_id)
    
    def save_to_db(self):
        if not self.in_db:
            if not self.validate():
                raise e.ContentInvalid.FeedbackInvalid(self.feedback.feedback_text, "Match not found")
            log(f"Creating feedback: ", "FeedbackService.save_to_db")
            MatchService.get_from_db(self.feedback.match_id).update_from_request(request=MatchUpdate(match_id=self.feedback.match_id, status_code=721, auth_uid=self.feedback.auth_uid))
            self.feedback.feedback_id = FeedbackDatabase.create_feedback(self.feedback)
        else:
            log(f"Updating feedback: ", "FeedbackService.save_to_db")
            self.update()
    
    @staticmethod
    def get_from_db(feedback_id: int):
        return FeedbackService(FeedbackDatabase.get_feedback(feedback_id))

    def update(self):
        if not self.validate():
            raise e.ContentInvalid.FeedbackInvalid("Invalid feedback data")
        FeedbackDatabase.update_feedback(self.feedback)
        log(f"Feedback {self.feedback.feedback_id} updated successfully", "FeedbackService.update")
    
    def validate(self):
        if Exists.match(self.feedback.match_id) and Exists.user(uid=self.feedback.auth_uid):
            return True
        return False
    
    @staticmethod
    @authorizeAdmin
    def create_feedback(data: Create):
        try:
            log(f"Creating feedback: ", "FeedbackService.create_feedback")
            feedback = FeedbackService(data.to_feedback())
            feedback.save_to_db()
            return feedback
        except Exception as e:
            logError("There was a problem creating feedback", e, "FeedbackService.create_feedback")
            raise
    
    @staticmethod
    @authorizeAdmin
    def update_feedback(data: Update):
        try:
            log(f"Updating feedback: ", "FeedbackService.update_feedback")
            feedback = FeedbackService(data.to_feedback(FeedbackDatabase.get_feedback(data.feedback_id)))
            feedback.update()
            return feedback
        except Exception as e:
            logError(e, "FeedbackService.update_feedback")
            raise
    
    @staticmethod
    def get_feedbacks(data: Get):
        try:
            log(f"Getting feedback: ", "FeedbackService.get_feedback")
            return_list = FeedbackDatabase.get_all_data()
            if data.all_feedback is True:
                log(f"Returning all feedbacks: ", "FeedbackService.get_feedback")
                return return_list
            if data.user_id:
                query = "SELECT * FROM feedback JOIN matches ON feedback.match_id = matches.match_id WHERE matches.uid = %s"
                db_data = Database.execute_query(query, (data.user_id,), fetch=True)
                log(f"Returning feedbacks for user: {data.user_id}", "FeedbackService.get_feedback")
                return_list = [FeedbackFactory.from_db_row(row) for row in db_data]
            params = data.generate_params()
            if params:
                db_data = FeedbackDatabase.find(params)
                feedback_ids = [feedback.feedback_id for feedback in db_data]
                log(f"Returning feedbacks with params: {params}, found={len(feedback_ids)}", "FeedbackService.get_feedback")
                return_list = [feedback for feedback in return_list if feedback.feedback_id in feedback_ids]
            if data.contains_feedback_text:
                log(f"Returning feedbacks containing text: {data.contains_feedback_text}", "FeedbackService.get_feedback")
                return_list = [feedback for feedback in return_list if data.contains_feedback_text in feedback.feedback_text]
            return return_list
        except Exception as e:
            logError("Error Getting Feedbacks", e, "FeedbackService.get_feedback")
            raise
    
    @staticmethod
    @authorizeAdmin
    def delete_feedback(feedback_id: int):
        try:
            log(f"Deleting feedback: ", "FeedbackService.delete_feedback")
            FeedbackDatabase.delete_feedback(feedback_id=feedback_id)
        except Exception as e:
            logError(e, "FeedbackService.delete_feedback")
            raise
    
    @staticmethod
    @authorizeAdmin
    def print_all(request):
        try:
            log(f"Printing all feedbacks: ", "FeedbackService.print_all")
            all_feedback = FeedbackDatabase.get_all_data()
            html_str = """
            <html>
            <head>
                <title>All Feedback</title>
                <style>
                    table {
                    font-family: Arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    }
                    
                    td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                    }
                    
                    tr:nth-child(even) {
                    background-color: #dddddd;
                    }
                    
                    th {
                    background-color: #f2f2f2;
                    }
                    
                    h1 {
                    text-align: center;
                    }
                    
                </style>
            </head>
            <body>
                <h1>All Feedback</h1>
                <table>
                    <tr>
                        <th>Feedback ID</th>
                        <th>Match ID</th>
                        <th>Feedback Text</th>
                        <th>Auth UID</th>
                    </tr>
            """
            for feedback in all_feedback:
                replaced_feedback_text = feedback.feedback_text.replace('\n', '<br>')
                html_str += f"""
                    <tr>
                        <td>{feedback.feedback_id}</td>
                        <td>{feedback.match_id}</td>
                        <td>{replaced_feedback_text}</td>
                        <td>{feedback.auth_uid}</td>
                    </tr>
                """
            html_str += """
                </table>
            </body>
            </html>
            """
            return html_str
        except Exception as e:
            logError(e, "FeedbackService.print_all")
            raise

