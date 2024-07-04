# region imports
import psycopg2
import psycopg2.pool
from psycopg2 import Error, OperationalError
from serverLogger import Logger
from typing import List
from datamodels import *
from factories import *
import traceback
# endregion

# region logging
def log(message, func):
    Logger.logDatabase(message, func)

def logError(e: Exception, func):
    error_message = f"\n{traceback.format_exception(None, e, e.__traceback__)}"
    message = f"An error occurred: {error_message}"
    Logger.logDatabase(message, func, "ERROR")
# endregion


# region Database
class Database:
    connection_pool = None

    @staticmethod
    def initialize():
        try:
            # Attempt to connect using the internal URL
            log("Connecting to internal URL", "Database.initialize")
            Database.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 90,
                database="resume_grader",
                user="bugslayerz",
                password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
                host="dpg-coi9t65jm4es739kjul0-a"
            )
            if Database.connection_pool:
                log("Connection to internal URL successful", "Database.initialize")
        except (Exception, psycopg2.DatabaseError) as internal_error:
            logError(internal_error, "Database.initialize")
            
            try:
                # Fallback to the external URL if internal fails
                Database.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 90,
                    database="resume_grader",
                    user="bugslayerz",
                    password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
                    host="dpg-coi9t65jm4es739kjul0-a.oregon-postgres.render.com"
                )
                if Database.connection_pool:
                    log("Connection to external URL successful", "Database.initialize")
            except (Exception, psycopg2.DatabaseError) as external_error:
                logError(external_error, "Database.initialize")

    @staticmethod
    def get_connection():
        return Database.connection_pool.getconn()

    @staticmethod
    def return_connection(connection):
        Database.connection_pool.putconn(connection)

    @staticmethod
    def execute_query(query, params=None, fetch=False):
        con = None
        try:
            con = Database.get_connection()
            with con.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    con.commit()
                    return result
                con.commit()
        except psycopg2.Error as e:
            logError(e, "execute_query")
            if con:
                con.rollback()
            raise
        finally:
            if con:
                Database.return_connection(con)

    @staticmethod
    def create_tables():
        try:
            log("Creating tables", "Database.create_tables")
            tables = {
                "users": """
                    CREATE TABLE users (
                        uid VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100),
                        dob VARCHAR(8),
                        is_owner BOOLEAN DEFAULT FALSE,
                        is_admin BOOLEAN DEFAULT FALSE,
                        phone_number CHAR(13),
                        email VARCHAR(100) NOT NULL UNIQUE
                    );
                """,
                "resumes": """
                    CREATE TABLE resumes (
                        uid VARCHAR(50) PRIMARY KEY,
                        skills TEXT[],
                        experience JSONB,
                        education JSONB,
                        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
                    );
                """,
                "jobdescriptions": """
                    CREATE TABLE jobdescriptions (
                        job_id SERIAL PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        company VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        required_skills TEXT[],
                        application_deadline VARCHAR(8),
                        location VARCHAR(100),
                        salary DECIMAL(10, 2),
                        job_type VARCHAR(4) CHECK (job_type IN ('FULL', 'PART', 'CONT', 'UNKN')),
                        active BOOLEAN DEFAULT TRUE
                    );
                """,
                "matches": """
                    CREATE TABLE matches (
                        match_id SERIAL PRIMARY KEY,
                        uid VARCHAR(50) NOT NULL,
                        job_id INT NOT NULL,
                        status VARCHAR(100)  DEFAULT 'Application received' NOT NULL,
                        status_code INT DEFAULT 100 NOT NULL,
                        grade DECIMAL(5, 2) DEFAULT 0 NOT NULL,
                        selected_skills TEXT[],
                        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
                        FOREIGN KEY (job_id) REFERENCES jobdescriptions(job_id) ON DELETE CASCADE
                    );
                """,
                "feedback": """
                    CREATE TABLE feedback (
                        feedback_id SERIAL PRIMARY KEY,
                        match_id INT NOT NULL,
                        feedback_text TEXT NOT NULL,
                        FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE
                    );
                """
            }
            for table_name, table_schema in tables.items().__reversed__():
                Database.execute_query(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            for table_name, table_schema in tables.items():
                Database.execute_query(table_schema)
            indexes = {
                "users": "CREATE INDEX idx_users_email ON users(email)",
                "users": "CREATE INDEX idx_users_uid ON users(uid)",
                "resumes": "CREATE INDEX idx_resumes_uid ON resumes(uid)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_title ON jobdescriptions(title)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_company ON jobdescriptions(company)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_description ON jobdescriptions(description)",
                "matches": "CREATE INDEX idx_matches_uid ON matches(uid)",
                "matches": "CREATE INDEX idx_matches_job_id ON matches(job_id)",
                "matches": "CREATE INDEX idx_matches_grade ON matches(grade)",
                "matches": "CREATE INDEX idx_matches_job_id_grade ON matches(job_id, grade)",
                "feedback": "CREATE INDEX idx_feedback_match_id ON feedback(match_id)"
            }
            log("Creating INDEXES", "Database.create_tables")
            for table_name, index_schema in indexes.items():
                Database.execute_query(index_schema)
            log("Tables and INDEXES created successfully", "Database.create_tables")
        except psycopg2.Error as e:
            logError(e, "Database.create_tables")
            raise
# endregion


# region UserDatabase
class UserDatabase:
    @staticmethod
    def create_user(user: User):
        try:
            log(f"Creating user {user.uid}", "UserDatabase.create_user")
            print(UserFactory.to_db_row(user))
            query = """
                INSERT INTO users (uid, name, dob, is_owner, is_admin, phone_number, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = UserFactory.to_db_row(user)
            Database.execute_query(query, params)
            log(f"User {user.uid} created successfully", "UserDatabase.create_user")
        except Exception as e:
            logError(e, "UserDatabase.create_user")
            raise

    @staticmethod
    def get_user(uid: str) -> User:
        try:
            log(f"Retrieving user {uid}", "UserDatabase.get_user")
            query = "SELECT * FROM users WHERE uid = %s"
            result = Database.execute_query(query, (uid,), fetch=True)
            if result:
                user = UserFactory.from_db_row(result[0])
                log(f"User {uid} retrieved successfully", "UserDatabase.get_user")
                return user
            else:
                raise ValueError(f"User {uid} not found")
        except Exception as e:
            logError(e, "UserDatabase.get_user")
            raise

    @staticmethod
    def update_user(user: User):
        try:
            log(f"Updating user {user.uid}", "UserDatabase.update_user")
            query = """
                UPDATE users SET name = %s, dob = %s, is_owner = %s, is_admin = %s, phone_number = %s, email = %s
                WHERE uid = %s
            """
            params = UserFactory.to_db_row(user, False) + (user.uid,)
            Database.execute_query(query, params)
            log(f"User {user.uid} updated successfully", "UserDatabase.update_user")
        except Exception as e:
            logError(e, "UserDatabase.update_user")
            raise

    @staticmethod
    def delete_user(uid: str):
        try:
            log(f"Deleting user {uid}", "UserDatabase.delete_user")
            query = "DELETE FROM users WHERE uid = %s"
            Database.execute_query(query, (uid,))
            log(f"User {uid} deleted successfully", "UserDatabase.delete_user")
        except Exception as e:
            logError(e, "UserDatabase.delete_user")
            raise

    @staticmethod
    def get_all_users() -> List[User]:
        try:
            log("Retrieving all users", "UserDatabase.get_all_users")
            query = "SELECT * FROM users"
            results = Database.execute_query(query, fetch=True)
            users = UserFactory.from_db_rows(results)
            log("All users retrieved successfully", "UserDatabase.get_all_users")
            return users
        except Exception as e:
            logError(e, "UserDatabase.get_all_users")
            raise
# endregion

# region ResumeDatabase
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
            params = ResumeFactory.to_db_row(resume, False) + (resume.uid,)
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
# endregion

# region JobDatabase
class JobDatabase:
    @staticmethod
    def create_job(job: Job):
        try:
            log(f"Creating job {job.title} at {job.company}", "JobDatabase.create_job")
            query = """
                INSERT INTO jobdescriptions (title, company, description, required_skills, application_deadline, location, salary, job_type, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = JobFactory.to_db_row(job)
            Database.execute_query(query, params)
            log(f"Job {job.title} at {job.company} created successfully", "JobDatabase.create_job")
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
            query = "SELECT * FROM jobdescriptions"
            results = Database.execute_query(query, fetch=True)
            jobs = JobFactory.from_db_rows(results)
            log("All jobs retrieved successfully", "JobDatabase.get_all_jobs")
            return jobs
        except Exception as e:
            logError(e, "JobDatabase.get_all_jobs")
            raise
# endregion

# region MatchDatabase
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
# endregion

# region FeedbackDatabase
class FeedbackDatabase:
    @staticmethod
    def create_feedback(feedback: Feedback):
        try:
            log(f"Creating feedback {feedback.feedback_id} for match {feedback.match_id}", "FeedbackDatabase.create_feedback")
            query = """
                INSERT INTO feedback (match_id, feedback_text)
                VALUES (%s, %s)
            """
            params = FeedbackFactory.to_db_row(feedback)
            Database.execute_query(query, params)
            log(f"Feedback {feedback.feedback_id} created successfully", "FeedbackDatabase.create_feedback")
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
                UPDATE feedback SET match_id = %s, feedback_text = %s
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

    @staticmethod
    def get_all_feedbacks() -> List[Feedback]:
        try:
            log("Retrieving all feedbacks", "FeedbackDatabase.get_all_feedbacks")
            query = "SELECT * FROM feedback"
            results = Database.execute_query(query, fetch=True)
            feedbacks = FeedbackFactory.from_db_rows(results)
            log("All feedbacks retrieved successfully", "FeedbackDatabase.get_all_feedbacks")
            return feedbacks
        except Exception as e:
            logError(e, "FeedbackDatabase.get_all_feedbacks")
            raise
# endregion


if __name__ == "__main__":
    Database.initialize()
    # Database.create_tables()
    '''user = User(
        uid="Slayerz.Wyld",
            name=Name(
                first_name="BS",
                last_name="Wyld"),
            dob=Date(
                day=22, 
                month=2, 
                year=2004), 
            is_admin=True, 
            is_owner=True, 
            phone_number="01-2046197621", 
            email="sidhuharijot@gmail.com")
    UserDatabase.create_user(user)'''
    '''resume = Resume(
        uid="Slayerz.Wyld", 
        skills=["Python", "Java"], 
        experience=[
            Experience(
                start_date=Date(
                    day=1, 
                    month=1, 
                    year=2020), 
                end_date=Date(
                    day=1, 
                    month=1, 
                    year=2021), 
                title="Software Developer", 
                company_name="Google", 
                description="Developed software"
                ), 
            Experience(
                start_date=Date(
                    day=1, 
                    month=1, 
                    year=2021), 
                end_date=Date(
                    day=1, 
                    month=1, 
                    year=2022), 
                title="Software Developer", 
                company_name="Microsoft", 
                description="Developed software")], 
        education=[
            Education(
                start_date=Date(
                    day=1, 
                    month=1, 
                    year=2018
                    ), 
                end_date=Date(
                    day=1, 
                    month=1, 
                    year=2022),
                institution="University of Manitoba", 
                course_name="Computer Science")
            ])
    ResumeDatabase.create_resume(resume)'''
    print(UserDatabase.get_all_users())
