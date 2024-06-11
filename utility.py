import openai
import os
import shutil
from pathlib import Path
import PyPDF2
import docx2txt
from dotenv import load_dotenv
from datamodels import *


# Load environment variables from .env file
load_dotenv()

class OpenAIUtility:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        openai.api_key = self.api_key

    def grade_resume(self, job_description: str, resume_data: str, max_grade: int):
        system_message = f"Grade resumes for this job description: \"{job_description}\" Maximum grade is {max_grade}. " + \
                         "Return -2 if resume is irrelevant to the job description. " + \
                         "Return -1 if job description is not understandable or if the resume data has nothing or is not understandable or enough to make a good judgement. " + \
                         "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Be harsh with your evaluations."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": resume_data}
            ]
        )
        return int(response.choices[0].message["content"].strip())

    def extract_resume_json(self, resume_text: str):
        system_message = """
        Convert the given resume data into a structured JSON format. Adhere strictly to this format:
        {
            "name": ["FirstName", "LastName"],
            "experience": [{"DDMMYYYY-DDMMYYYY": {["JOB TITLE", "COMPANY NAME"]]: "DESCRIPTION"}}, {"DDMMYYYY-DDMMYYYY": {["JOB TITLE", "COMPANY NAME"]: "DESCRIPTION"}}],
            "skills": ["skill1", "skill2"],
            "education": [{"DDMMYYYY-DDMMYYYY": {"INSTITUTION": "COURSE NAME"}}]
        }
        Dates must be formatted as DDMMYYYY or 00000000 if no date is available.
        Ensure the phone number format includes a hyphen between the country code and the number.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": resume_text}
            ]
        )
        return response.choices[0].message["content"]

    def extract_job_description_json(self, job_description_text: str):
        system_message = """
        Convert the given job description data into a structured JSON format. Adhere strictly to this format:
        {
            "Title": "Job Title",
            "description": "Job Description",
            "employer": "Employer Name",
            "Must Haves": ["Requirement 1", "Requirement 2"]
        }
        Ensure that the job description is concise and clearly describes the role, responsibilities, and requirements for the position.
        For must-have requirements, list them only if given in the job description. Must haves are the responsibilities or requirements that are mandatory for the job.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": job_description_text}
            ]
        )
        return response.choices[0].message["content"]

class FileUtility:
    TEMP_DIR = Path("temp_files")
    
    @staticmethod
    def initialize_temp_dir():
        FileUtility.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_temp_file(file) -> Path:
        temp_file_path = FileUtility.TEMP_DIR / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return temp_file_path

    @staticmethod
    def extract_text(file_path: Path) -> str:
        if file_path.suffix == '.pdf':
            return FileUtility._extract_text_from_pdf(file_path)
        elif file_path.suffix == '.docx':
            return FileUtility._extract_text_from_docx(file_path)
        else:
            return FileUtility._extract_text_from_txt(file_path)

    @staticmethod
    def _extract_text_from_pdf(file_path: Path) -> str:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return ''.join([page.extract_text() for page in reader.pages])

    @staticmethod
    def _extract_text_from_docx(file_path: Path) -> str:
        return docx2txt.process(str(file_path))

    @staticmethod
    def _extract_text_from_txt(file_path: Path) -> str:
        with file_path.open("r", encoding='utf-8') as file:
            return file.read()

