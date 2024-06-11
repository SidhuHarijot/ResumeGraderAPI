import email_validator
from datamodels import User, Resume, Job, Match, Feedback
from authorize import Authorize

class Validation:
    @staticmethod
    def validate_email(email: str) -> bool:
        try:
            email_validator.validate_email(email, check_deliverability=False)
            return True
        except email_validator.EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        if len(phone_number) == 13 and phone_number[2] == "-" and (phone_number[:2] + phone_number[3:]).isnumeric():
            return True
        return False

    @staticmethod
    def validate_date(date: str) -> bool:
        return len(date) == 8 and date.isnumeric()

    @staticmethod
    def validate_name(name: str) -> bool:
        return name.isalpha() and 2 <= len(name) <= 50

    @staticmethod
    def validate_user(user: User) -> bool:
        if not Validation.validate_email(user.email):
            return False
        if not Validation.validate_phone_number(user.phone_number):
            return False
        if not Validation.validate_name(user.name.first_name):
            return False
        if not Validation.validate_name(user.name.last_name):
            return False
        if not Validation.validate_date(user.dob):
            return False
        return True

    @staticmethod
    def validate_resume(resume: Resume) -> bool:
        if not resume.uid:
            return False
        for skill in resume.skills:
            if not isinstance(skill, str) or not skill:
                return False
        for experience in resume.experience:
            if not Validation.validate_date(experience.start_date) or not Validation.validate_date(experience.end_date):
                return False
        for education in resume.education:
            if not Validation.validate_date(education.start_date) or not Validation.validate_date(education.end_date):
                return False
        return True

    @staticmethod
    def validate_job(job: Job) -> bool:
        if not job.title or not isinstance(job.title, str):
            return False
        if not job.company or not isinstance(job.company, str):
            return False
        if not job.description or not isinstance(job.description, str):
            return False
        if not all(isinstance(skill, str) for skill in job.required_skills):
            return False
        if not Validation.validate_date(job.application_deadline):
            return False
        if not isinstance(job.location, str) or not job.location:
            return False
        if not isinstance(job.salary, float):
            return False
        if job.job_type not in ['FULL', 'PART', 'CONT', 'UNKN']:
            return False
        if not isinstance(job.active, bool):
            return False
        return True

    @staticmethod
    def validate_match(match: Match) -> bool:
        if not match.uid or not isinstance(match.uid, str):
            return False
        if not match.job_id or not isinstance(match.job_id, int):
            return False
        if not match.status or not isinstance(match.status, str):
            return False
        if not isinstance(match.status_code, int):
            return False
        if not isinstance(match.grade, float):
            return False
        if not all(isinstance(skill, str) for skill in match.selected_skills):
            return False
        return True

    @staticmethod
    def validate_feedback(feedback: Feedback) -> bool:
        if not feedback.match_id or not isinstance(feedback.match_id, int):
            return False
        if not feedback.feedback_text or not isinstance(feedback.feedback_text, str):
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
