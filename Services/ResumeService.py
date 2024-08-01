from .services import log, logError
from Database.GetDatabases import ResumeDatabase
from Models.DataModels.GetModels import Resume
from Models.RequestModels.GetModels import RequestModels as rm
from Processing.Factories.GetFactories import ResumeFactory
from Utilities.GetUtilities import OpenAIUtility, FileUtility
from fastapi import UploadFile
from Processing.authorize import authorizeAdmin
from .MatchService import MatchService
from Models.RequestModels.GetModels import RequestModels as rm
from Errors.GetErrors import Errors as e
from Database.check import Exists


class ResumeService:
    resume: Resume = None
    in_db = False

    def __init__(self, resume: Resume = None, dict: dict = None, json_str: str = None, db_row: str = None):
        if dict or json_str:
            resume = ResumeFactory.from_json(json_str)
        elif db_row:
            resume = ResumeFactory.from_db_row(db_row)
        if resume:
            self.resume = resume
            self.check_in_db()
        else:
            raise ValueError("No valid arguments provided to ResumeService constructor")
    
    def check_in_db(self):
        try:
            ResumeDatabase.get_resume(self.resume.uid)
            self.in_db = True
        except ValueError:
            self.in_db = False
            log(f"Resume not found in database: {self.resume.uid}", "ResumeService.check_in_db")
        return self.in_db
    
    def save_to_db(self):
        if not self.in_db:
            self.validate()
            ResumeDatabase.create_resume(self.resume)
        else:
            self.update()
    
    def update(self, request: rm.Resumes.Update = None):
        if request:
            self.resume = request.to_resume(self.resume)
            self.validate()
        MatchService.put_for_re_evaluation(self.resume.uid)
        ResumeDatabase.update_resume(self.resume)

    def to_json(self):
        return ResumeFactory.to_json(self.resume)
    
    @staticmethod
    def create_from_request(request: rm.Resumes.Create, file = None):
        if file is not None:
            resume = ResumeService.process_resume(file)
        else:
            resume = request.to_resume()
        resume.uid = request.uid
        rs = ResumeService(resume)
        rs.save_to_db()
        return rs

    @staticmethod
    def create_from_db(uid: str):
        return ResumeService(ResumeDatabase.get_resume(uid))

    @staticmethod
    def process_resume(file: UploadFile = None) -> Resume:
        log("Processing resume", "ResumeService.process_resume")
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            resume_text = FileUtility.extract_text(temp_file_path)
            resume_json = OpenAIUtility.extract_resume_json(resume_text)
            print(resume_json)
            resume_data = ResumeFactory.from_json(resume_json)
            log(f"Resume processed: {resume_data.uid}", "ResumeService.process_resume")
            return resume_data
    
    def validate(self):
        if not Exists.user(self.resume.uid):
            raise e.ContentInvalid.UIDInvalid(self.resume.uid, "UID does not exist in the database")
    
    def delete(self):
        ResumeDatabase.delete_resume(self.resume.uid)
        self.in_db = False

    @staticmethod
    def delete_from_db(uid: str):
        ResumeDatabase.delete_resume(uid)
    
    @staticmethod
    def get_from_job(job_id):
        return ResumeDatabase.find_with_join("JOIN matches ON resumes.uid = matches.uid", {"job_id": job_id})

    @staticmethod
    @authorizeAdmin
    def print_all(request):
        log("Printing all resumes", "print_all")
        try:
            resumes = ResumeDatabase.get_all_resumes()
            html_data = """
            <html>
            <head>
                <title>All Resumes</title>
                <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                </style>
            </head>
            <body>
                <h1>All Resumes</h1>
                <table>
                    <tr>
                        <th>UID</th>
                        <th>Skills</th>
                        <th>Education</th>
                        <th>Experience</th>
                    </tr>
            """
            for resume in resumes:
                html_data += f"""
                    <tr>
                        <td>{resume.uid}</td>
                        <td>
                """
                for skill in resume.skills:
                    html_data += f"# {skill}<br>"
                html_data += "</td><td>"
                for education in resume.education:
                    html_data += f"{education.course_name} from {education.institution}<br>"
                html_data += "</td><td>"
                for experience in resume.experience:
                    html_data += f"{experience.title} at {experience.company_name}<br>"
                html_data += "</td></tr>"
            html_data += """
                </table>
            </body>
            </html>
            """
            return html_data
        except Exception as e:
            logError("Error in ResumeService print_all", e, "print_all")
            raise
    
    