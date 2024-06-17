import email_validator
from datamodels import User, Resume, Job, Match, Feedback
from authorize import Authorize
from serverLogger import Logger
import traceback


def log(msg, func):
    Logger.logValidation(msg, func)

def logError(msg, func):
    Logger.logValidation(msg, func, "ERROR")


class Validation:
    @staticmethod
    def validate_email(email: str) -> bool:
        try:
            validated_email = email_validator.validate_email(email, check_deliverability=False)
            if not validated_email.normalized == email:
                return False
            return True
        except email_validator.EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        if len(phone_number) == 13 and phone_number[2] == "-" and (phone_number[:2] + phone_number[3:]).isnumeric():
            return True
        return False


    @staticmethod
    def validate_user(user: User) -> bool:
        log(f"Validating user: {str(user.name)}", "Validation.validate_user")
        if not Validation.validate_email(user.email):
            logError(f"Invalid email {str(user.name)}", "Validation.validate_user")
            return False
        if not Validation.validate_phone_number(user.phone_number):
            logError(f"Invalid phone number {str(user.name)}", "Validation.validate_user")
            return False
        log(f"User {str(user.name)} is valid", "Validation.validate_user")
        return True

    @staticmethod
    def validate_resume(resume: Resume) -> bool:
        if not resume.uid:
            return False
        for skill in resume.skills:
            if not isinstance(skill, str) or not skill:
                return False
        return True

    @staticmethod
    def validate_job(job: Job) -> bool:
        log(f"Validating job: {str(job.title)}", "Validation.validate_job")
        if not job.title or not isinstance(job.title, str):
            logError(f"Invalid title {str(job.title)}", "Validation.validate_job")
            return False
        if not job.company or not isinstance(job.company, str):
            logError(f"Invalid company {str(job.title)}", "Validation.validate_job")
            return False
        if not job.description or not isinstance(job.description, str):
            logError(f"Invalid description {str(job.title)}", "Validation.validate_job")
            return False
        if not all(isinstance(skill, str) for skill in job.required_skills):
            logError(f"Invalid required skills {str(job.title)}", "Validation.validate_job")
            return False
        if not isinstance(job.location, str) or not job.location:
            logError(f"Invalid location {str(job.title)}", "Validation.validate_job")
            return False
        if not isinstance(job.salary, float):
            logError(f"Invalid salary {str(job.title)}", "Validation.validate_job")
            return False
        if job.job_type not in ['FULL', 'PART', 'CONT', 'UNKN']:
            logError(f"Invalid job type {str(job.title)}", "Validation.validate_job")
            return False
        if not isinstance(job.active, bool):
            logError(f"Invalid active status {str(job.title)}", "Validation.validate_job")
            return False
        return True

    @staticmethod
    def validate_match(match: Match) -> bool:
        log(f"Validating match: {str(match.uid)}", "Validation.validate_match")
        if not match.uid or not isinstance(match.uid, str):
            logError(f"Invalid user ID {str(match.uid)}", "Validation.validate_match")
            return False
        if not match.job_id or not isinstance(match.job_id, int):
            logError(f"Invalid job ID {str(match.uid)}", "Validation.validate_match")
            return False
        if not match.status or not isinstance(match.status, str):
            logError(f"Invalid status {str(match.uid)}", "Validation.validate_match")
            return False
        if not isinstance(match.status_code, int):
            logError(f"Invalid status code {str(match.uid)}", "Validation.validate_match")
            return False
        if not isinstance(match.grade, float):
            logError(f"Invalid grade {str(match.uid)}", "Validation.validate_match")
            return False
        if not all(isinstance(skill, str) for skill in match.selected_skills):
            logError(f"Invalid selected skills {str(match.uid)}", "Validation.validate_match")
            return False
        return True

    @staticmethod
    def validate_feedback(feedback: Feedback) -> bool:
        log(f"Validating feedback: {str(feedback.match_id)}", "Validation.validate_feedback")
        if not feedback.match_id or not isinstance(feedback.match_id, int):
            logError(f"Invalid match ID {str(feedback.match_id)}", "Validation.validate_feedback")
            return False
        if not feedback.feedback_text or not isinstance(feedback.feedback_text, str):
            logError(f"Invalid feedback text {str(feedback.match_id)}", "Validation.validate_feedback")
            return False
        return True

    @staticmethod
    def check_is_admin(uid: str) -> bool:
        return Authorize.checkAuth(uid, "ADMIN")

    @staticmethod
    def check_is_owner(uid: str) -> bool:
        return Authorize.checkAuth(uid, "OWNER")


if __name__ == "__main__":
    from datamodels import Name, Date, User
    # Test cases for validation functions
    user = User(
        uid="123",
        name=Name(first_name="John", last_name="Doe"),
        dob="01011999",
        is_owner=True,
        is_admin=False,
        phone_number="91-9876543210",
        email="john.doe@example.com"
    )
    print(Validation.validate_user(user))
    print(Validation.validate_phone_number("91-9876543210"))
    print(Validation.validate_phone_number("919876543210"))
    print(Validation.validate_email("invalid@domain"))
