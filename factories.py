from datamodels import *
from serverLogger import Logger
from typing import List
import json
import traceback


def log(message, func):
    Logger.logFactories(message, func)

def logError(log, e: Exception, func):
    error_message = "".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
    message = f"{log}: {str(e)}\n{error_message}"
    Logger.logFactories(message, func, "ERROR")


class UserFactory:
    @staticmethod
    def from_db_row(row) -> User:
        try:
            log(f"Creating User object from row: {row[1]}", "UserFactory.from_db_row")
            return User(
                uid=row[0],
                name=Name.from_string(row[1]),
                dob=Date.from_string(row[2]),
                is_owner=row[3],
                is_admin=row[4],
                phone_number=row[5],
                email=row[6]
            )
        except Exception as e:
            logError(f"Error creating User object from row: {row}. \n", e, "UserFactory.from_db_row")
            return User(uid=row[0], name=Name(first_name="Error", last_name="Error"), dob=Date(day=1, month=1, year=1), is_owner=False, is_admin=False, phone_number="00-0000000000", email="error@database.com")
            

    @staticmethod
    def to_db_row(user: User, with_uid=True):
        try:
            log(f"Converting User object to db row: {str(user.name)}", "UserFactory.to_db_row")
            dob_str = str(user.dob)
            if with_uid:
                return (
                    user.uid,
                    str(user.name),
                    dob_str,
                    user.is_owner,
                    user.is_admin,
                    user.phone_number,
                    user.email
                )
            return (
                str(user.name),
                dob_str,
                user.is_owner,
                user.is_admin,
                user.phone_number,
                user.email
            )
        except Exception as e:
            logError(f"Error converting User object to db row: {user}. \n", e, "UserFactory.to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> User:
        try:
            log(f"Creating User object from JSON: {data['name']}", "UserFactory.from_json")
            try:
                name = Name.from_string(data['name'])
            except TypeError:
                data = json.loads(data)
                name = Name.from_string(data['name'])
            return User(
                uid=data['uid'],
                name=name,
                dob=Date.from_string(data['dob']),
                is_owner=data.get('is_owner', False),
                is_admin=data.get('is_admin', False),
                phone_number=data['phone_number'],
                email=data['email']
            )
        except Exception as e:
            logError(f"Error creating User object from JSON: {data}. \n", e, "UserFactory.from_json")
            raise

    @staticmethod
    def to_json(user: User) -> dict:
        try:
            log(f"Converting User object to JSON: {str(user.name)}", "UserFactory.to_json")
            return {
                'uid': user.uid,
                'name': str(user.name),
                'dob': str(user.dob),
                'is_owner': user.is_owner,
                'is_admin': user.is_admin,
                'phone_number': user.phone_number,
                'email': user.email
            }
        except Exception as e:
            logError(f"Error converting User object to JSON: {user}. \n", e, "UserFactory.to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[User]:
        try:
            log(f"Creating list of User objects from multiple rows: ", "UserFactory.from_db_rows")
            result = []
            return [UserFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of User objects from rows. \n", e, "UserFactory.from_db_rows")
            raise

    @staticmethod
    def to_db_rows(users: List[User]) -> List[tuple]:
        try:
            log(f"Converting list of User objects to db rows: ", "UserFactory.to_db_rows")
            return [UserFactory.to_db_row(user) for user in users]
        except Exception as e:
            logError(f"Error converting list of User objects to db rows. \n", e, "UserFactory.to_db_rows")
            raise


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
                application_deadline=Date.from_string(row[5]),
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
            if job.job_id == -1 or not with_id:
                return (
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
            return (
                job.job_id,
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
        except Exception as e:
            logError(f"Error converting Job object to db row: {job} at {job}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Job:
        try:
            log(f"Creating Job object from JSON: {data['title']} at {data['company']}", "from_json")
            try:
                job_id = data['job_id']
            except TypeError:
                data = json.loads(data)
                job_id = data['job_id']
            return Job(
                job_id=job_id,
                title=data['title'],
                company=data['company'],
                description=data['description'],
                required_skills=data['required_skills'],
                application_deadline=Date.from_string(data['application_deadline']),
                location=data['location'],
                salary=data['salary'],
                job_type=data['job_type'],
                active=data['active']
            )
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


class MatchFactory:
    @staticmethod
    def from_db_row(row) -> Match:
        try:
            log(f"Creating Match object from row: {row[1]}", "from_db_row")
            return Match(
                match_id=row[0],
                uid=row[1],
                job_id=row[2],
                status=row[3],
                status_code=row[4],
                grade=row[5],
                selected_skills=row[6]
            )
        except Exception as e:
            logError(f"Error creating Match object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(match: Match, with_id=True):
        try:
            log(f"Converting Match object to db row: {match.match_id}", "to_db_row")

            if not with_id:
                return (
                    match.uid,
                    match.job_id,
                    match.status,
                    match.status_code,
                    match.grade,
                    match.selected_skills
                )
            return (
                match.match_id,
                match.uid,
                match.job_id,
                match.status,
                match.status_code,
                match.grade,
                match.selected_skills
            )
        except Exception as e:
            logError(f"Error converting Match object to db row: {match}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Match:
        try:
            log(f"Creating Match object from JSON: {data['match_id']}", "from_json")
            try:
                match_id = data['match_id']
            except TypeError:
                data = json.loads(data)
                match_id = data['match_id']
            return Match(
                match_id=match_id,
                uid=data['uid'],
                job_id=data['job_id'],
                status=data['status'],
                status_code=data['status_code'],
                grade=data['grade'],
                selected_skills=data.get('selected_skills')
            )
        except Exception as e:
            logError(f"Error creating Match object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(match: Match) -> dict:
        try:
            log(f"Converting Match object to JSON: {match.match_id}", "to_json")
            return {
                'match_id': match.match_id,
                'uid': match.uid,
                'job_id': match.job_id,
                'status': match.status,
                'status_code': match.status_code,
                'grade': match.grade,
                'selected_skills': match.selected_skills
            }
        except Exception as e:
            logError(f"Error converting Match object to JSON: {match}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Match]:
        try:
            log(f"Creating list of Match objects from multiple rows: ", "from_db_rows")
            return [MatchFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Match objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(matches: List[Match]) -> List[tuple]:
        try:
            log(f"Converting list of Match objects to db rows: ", "to_db_rows")
            return [MatchFactory.to_db_row(match) for match in matches]
        except Exception as e:
            logError(f"Error converting list of Match objects to db rows. \n", e, "to_db_rows")
            raise


class FeedbackFactory:
    @staticmethod
    def from_db_row(row) -> Feedback:
        try:
            log(f"Creating Feedback object from row: {row[1]}", "from_db_row")
            return Feedback(
                feedback_id=row[0],
                match_id=row[1],
                feedback_text=row[2]
            )
        except Exception as e:
            logError(f"Error creating Feedback object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(feedback: Feedback, with_id=True):
        try:
            log(f"Converting Feedback object to db row: {feedback.feedback_id}", "to_db_row")
            if not with_id:
                return (
                    feedback.match_id,
                    feedback.feedback_text
                )
            return (
                feedback.feedback_id,
                feedback.match_id,
                feedback.feedback_text
            )
        except Exception as e:
            logError(f"Error converting Feedback object to db row: {feedback}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Feedback:
        try:
            log(f"Creating Feedback object from JSON: {data['feedback_id']}", "from_json")
            try:
                feedback_id = data['feedback_id']
            except TypeError:
                data = json.loads(data)
                feedback_id = data['feedback_id']
            return Feedback(
                feedback_id=feedback_id,
                match_id=data['match_id'],
                feedback_text=data['feedback_text']
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
                'feedback_text': feedback.feedback_text
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


class ExperienceFactory:
    @staticmethod
    def to_json(experience: Experience) -> dict:
        try:
            log(f"Converting Experience object to JSON: {experience.title}", "to_json")
            return {
                'start_date': str(experience.start_date),
                'end_date': str(experience.end_date),
                'title': experience.title,
                'company_name': experience.company_name,
                'description': experience.description
            }
        except Exception as e:
            logError(f"Error converting Experience object to JSON: {experience}. \n", e, "to_json")
            raise
    
    @staticmethod
    def from_json(data: dict) -> Experience:
        try:
            log(f"Creating Experience object from JSON: {data['title']}", "from_json")
            return Experience(
                start_date=Date.from_string(data['start_date']),
                end_date=Date.from_string(data['end_date']),
                title=data['title'],
                company_name=data['company_name'],
                description=data['description']
            )
        except TypeError:
            log("Data is not a dictionary. Converting to json dict.", "from_json")
            try:
                data = json.loads(data)
                return Experience(
                    start_date=Date.create_from_input(data['start_date']),
                    end_date=Date.create_from_input(data['end_date']),
                    title=data['title'],
                    company_name=data['company_name'],
                    description=data['description']
                )
            except Exception as e:
                logError(f"Error creating Experience object from JSON: {data}. \n", e, "from_json")
                raise
        except Exception as e:
            logError(f"Error creating Experience object from JSON: {data}. \n", e, "from_json")
            raise
    
    @staticmethod
    def bulk_to_json(experiences: List[Experience]) -> List[dict]:
        try:
            log(f"Converting list of Experience objects to JSON: ", "bulk_to_json")
            return [ExperienceFactory.to_json(exp) for exp in experiences]
        except Exception as e:
            logError(f"Error converting list of Experience objects to JSON. \n", e, "to_json")
            raise
    
    @staticmethod
    def build_from_json(data: List[dict]) -> List[Experience]:
        try:
            log(f"Creating list of Experience objects from JSON: ", "build_from_json")
            return [ExperienceFactory.from_json(exp) for exp in data]
        except Exception as e:
            logError(f"Error creating list of Experience objects from JSON. \n", e, "from_json")
            raise


class EducationFactory:
    @staticmethod
    def to_json(education: Education) -> dict:
        try:
            log(f"Converting Education object to JSON: {education.course_name}", "to_json")
            return {
                'start_date': str(education.start_date),
                'end_date': str(education.end_date),
                'institution': education.institution,
                'course_name': education.course_name
            }
        except Exception as e:
            logError(f"Error converting Education object to JSON: {education}. \n", e, "to_json")
            raise
    
    @staticmethod
    def from_json(data: dict) -> Education:
        try:
            log(f"Creating Education object from JSON: {data['course_name']}", "from_json")
            try:
                course_name = data['course_name']
            except TypeError:
                data = json.loads(data)
                course_name = data['course_name']
            return Education(
                start_date=Date.from_string(data['start_date']),
                end_date=Date.from_string(data['end_date']),
                institution=data['institution'],
                course_name=course_name
            )
        except Exception as e:
            logError(f"Error creating Education object from JSON: {data}. \n", e, "from_json")
            raise
    
    @staticmethod
    def bulk_to_json(educations: List[Education]) -> List[dict]:
        try:
            log(f"Converting list of Education objects to JSON: ", "bulk_to_json")
            return [EducationFactory.to_json(edu) for edu in educations]
        except Exception as e:
            logError(f"Error converting list of Education objects to JSON. \n", e, "to_json")
            raise
    
    @staticmethod
    def build_from_json(data: List[dict]) -> List[Education]:
        try:
            log(f"Creating list of Education objects from JSON: ", "build_from_json")
            return [EducationFactory.from_json(edu) for edu in data]
        except Exception as e:
            logError(f"Error creating list of Education objects from JSON. \n", e, "from_json")
            raise


class ResumeFactory:
    @staticmethod
    def from_db_row(row) -> Resume:
        try:
            log(f"Creating Resume object from row: {row[1]}", "from_db_row")
            return Resume(
                uid=row[1],
                skills=row[2],
                experience=ExperienceFactory.build_from_json(row[3]),
                education=EducationFactory.build_from_json(row[4])
            )
        except Exception as e:
            logError(f"Error creating Resume object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(resume: Resume):
        try:
            log(f"Converting Resume object to db row: {resume.uid}", "to_db_row")

            return (
                resume.uid,
                resume.skills,
                json.dumps(ExperienceFactory.bulk_to_json(resume.experience)),
                json.dumps(EducationFactory.bulk_to_json(resume.education))
            )
        except Exception as e:
            logError(f"Error converting Resume object to db row: {resume}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Resume:
        try:
            log(f"Creating Resume object from JSON: {data['uid']}", "from_json")
            try:
                uid = data['uid']
            except TypeError:
                data = json.loads(data)
                uid = data['uid']
            return Resume(
                uid=uid,
                skills=data['skills'],
                experience=ExperienceFactory.build_from_json(data['experience']),
                education=EducationFactory.build_from_json(data['education'])
            )
        except Exception as e:
            logError(f"Error creating Resume object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(resume: Resume) -> dict:
        try:
            log(f"Converting Resume object to JSON: {resume.uid}", "to_json")
            return {
                'uid': resume.uid,
                'skills': resume.skills,
                'experience': ExperienceFactory.bulk_to_json(resume.experience),
                'education': EducationFactory.bulk_to_json(resume.education)
            }
        except Exception as e:
            logError(f"Error converting Resume object to JSON: {resume}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Resume]:
        try:
            log(f"Creating list of Resume objects from rows: ", "from_db_rows")
            return [ResumeFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Resume objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(resumes: List[Resume]) -> List[tuple]:
        try:
            log(f"Converting list of Resume objects to db rows: ", "to_db_rows")
            return [ResumeFactory.to_db_row(resume) for resume in resumes]
        except Exception as e:
            logError(f"Error converting list of Resume objects to db rows. \n", e, "to_db_rows")
            raise


if __name__ == "__main__":
    resume = Resume(uid="fff", skills=["f", "h"], experience=[Experience(start_date=Date(day=1, month=1, year=2020), end_date=Date(day=1, month=1, year=2021), title="title", company_name="company", description="desc")], education=[Education(start_date=Date(day=1, month=1, year=2020), end_date=Date(day=1, month=1, year=2021), institution="inst", course_name="course")])
    db_row = ResumeFactory.to_db_row(resume)
    print(db_row)
    resume = ResumeFactory.from_db_row(db_row)
    print(resume)