from fastapi import UploadFile
from Utilities.GetUtilities import OpenAIUtility, FileUtility
from Models.DataModels.GetModels import Job
from Processing.Factories.GetFactories import JobFactory
from .services import log, logError
from Database.GetDatabases import JobDatabase
from Processing.authorize import authorizeAdmin, authorizeOwner
from Models.RequestModels.GetModels import RequestModels as rm

    
class JobService:
    job: Job = None

    def __init__(self, job: Job = None, dict: dict = None, json_str: str = None, db_row: str = None):
        if dict or json_str:
            job = JobFactory.from_json(json_str)
        elif db_row:
            job = JobFactory.from_db_row(db_row)
        if job:
            self.job = job
        else:
            raise ValueError("No valid arguments provided to JobService constructor")

    def save_to_db(self):
        if not self.validate():
            raise ValueError("Invalid job data")
        self.job.job_id = JobDatabase.create_job(self.job)
    
    def to_text(self, exclude=[]):
        return JobFactory.to_text(self.job, exclude=exclude)
    
    @staticmethod
    def get_from_db(job_id: int):
        return JobService(JobDatabase.get_job(job_id))
    
    @staticmethod
    def delete_from_db(job_id: int):
        JobDatabase.delete_job(job_id)
    
    @staticmethod
    @authorizeAdmin
    def create_from_request(request: rm.Jobs.Create, file: UploadFile = None):
        if file:
            job = JobService.process_job_description(file)
        else:
            job = JobService(request.to_job())
        job.save_to_db()
        return job
    
    @authorizeAdmin
    def update(self, request: rm.Jobs.Update = None):
        if request:
            self.job = request.to_job(self.job)
        if not self.validate():
            raise ValueError("Invalid job data")
        JobDatabase.update_job(self.job)
    
    def validate(self):
        return True
    
    def delete(self):
        JobDatabase.delete_job(self.job.job_id)

    @staticmethod
    def process_job_description(file: UploadFile = None) -> Job:
        log("Processing job description", "JobService.process_job_description")
        if file:
            FileUtility.initialize_temp_dir()
            temp_file_path = FileUtility.save_temp_file(file)
            job_description_text = FileUtility.extract_text(temp_file_path)

            job_json = OpenAIUtility.extract_job_description_json(job_description_text)
            job_data = JobFactory.from_json(job_json)
            log(f"Job description processed: {job_data.job_id}", "JobService.process_job_description")
            return JobService(job_data)
        else:
            logError("No file provided to process_job_description", ValueError("No file provided to process_job_description"), "JobService.process_job_description")
            raise ValueError("No file provided to process_job_description")
        
    @staticmethod
    def get_multiple_jobs_from_db(request: rm.Jobs.Get):
        if request.active is not None:
            all_jobs = JobDatabase.find_jobs({"active": request.active})
        else:
            all_jobs = JobDatabase.get_all_jobs()
        if request.skills:
            all_jobs = [job for job in all_jobs if all(skill.upper() in [skill.upper() for skill in job.required_skills] for skill in request.skills)]
        return all_jobs
    
    @staticmethod
    @authorizeAdmin
    def print_all(request):
        log("Printing all jobs", "JobService.print_all")
        try:
            all_jobs = JobDatabase.get_all_jobs()
            html_data = """
            <html>
            <head>
                <title>All Jobs</title>
                <style>
                table {
                    font-family: Arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                }

                th {
                    background-color: #f2f2f2;
                }

                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }

                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }

                </style>
            </head>
            <body>
            <h1>All Jobs</h1>
            <table>
                <tr>
                    <th>Job ID</th>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Salary</th>
                    <th>Job Type</th>
                    <th>Required Skills</th>
                    <th>Active</th>
                </tr>
            """
            for job in all_jobs:
                html_data += f"""
                <tr>
                    <td>{job.job_id}</td>
                    <td>{job.title}</td>
                    <td>{job.company}</td>
                    <td>{job.location}</td>
                    <td>{job.salary}</td>
                    <td>{job.job_type}</td>
                    <td>{", <br>".join(job.required_skills)}</td>
                    <td>{job.active}</td>
                </tr>
                """
            html_data += """
            </table>
            </body>
            </html>
            """
            return html_data
        except Exception as e:
            logError("Error in JobService print_all", e, "print_all")
            raise

        