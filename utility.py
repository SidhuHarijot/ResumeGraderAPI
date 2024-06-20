import openai
import os
import shutil
from pathlib import Path
import PyPDF2
import docx2txt
from dotenv import load_dotenv
from datamodels import *
from serverLogger import Logger
import traceback
import json
import re


def log(msg, func):
    Logger.logService(msg, func)

def logError(msg, exception, func):
    msg = f"{msg}. Exception: {''.join(traceback.format_exception(None, exception, exception.__traceback__))}"
    Logger.logService(msg, func, "ERROR")


# Load environment variables from .env file
load_dotenv()

class OpenAIUtility:
    @classmethod
    def initialize(self):
        log("Initializing OpenAI Utility", "OpenAIUtility.__init__")
        if not os.environ["OPENAI_API_KEY"]:
            raise ValueError("OpenAI API key not found in environment variables.")
        openai.api_key = os.environ["OPENAI_API_KEY"]
        log("OpenAI Utility initialized", "OpenAIUtility.__init__")
    

    @classmethod
    def getResponse(self, systemMessage, userMessage, responseType, min_val=-1, max_val=-1):
        gpt_response_type = {"type": "text"}
        if responseType == "dict":
            gpt_response_type = {"type": "json_object"}
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": systemMessage},
                {"role": "user", "content": userMessage},
            ],
            response_format=gpt_response_type
        )
        response = response.choices[0].message["content"]
        if isinstance(response, dict):
            return response
        if isinstance(response, str):
            if responseType == "dict":
                return json.loads(response)
            elif responseType == "str":
                return response
            elif responseType == "int":
                return int(self.extractNumericResponse(response, min_val, max_val))
            elif responseType == "float":
                return float(self.extractNumericResponse(response, min_val, max_val))
            else:
                return response
    

    @classmethod
    def extractNumericResponse(self, response, min_val, max_val):

        def extractNumbers(response, min_val, max_val):
            spliced_text = response.replace("\n", " ").split(" ")
            numbers = []
            for text in spliced_text:
                if text.replace(".", "").isdigit():
                    if not min_val == -1 and not max_val == -1:
                        if float(text) >= min_val and float(text) <= max_val:
                            numbers.append(float(text))
                    else:
                        numbers.append(float(text))
            return numbers

        try:
            return float(response)
        except ValueError as e:
            try:
                return extractNumbers(response, min_val, max_val)[0]
            except Exception as e:
                logError("Error extracting int response", e, "OpenAIUtility.extractIntResponse")
                return -1
        except Exception as e:
            logError("Error extracting int response", e, "OpenAIUtility.extractIntResponse")
            return -1

    @classmethod
    def grade_resume(self, job_description: str, resume_data: str, max_grade: int):
        log(f"Grading resume for job description: {job_description}", "OpenAIUtility.grade_resume")
        system_message = f"Grade resumes for this job description: \"{job_description}\" Maximum grade is {max_grade}. " + \
                         "Return -2 if resume is irrelevant to the job description. " + \
                         "Return -1 if job description is not understandable or if the resume data has nothing or is not understandable or enough to make a good judgement. " + \
                         "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Be harsh with your evaluations."
        response = self.getResponse(system_message, resume_data, "int", -2, max_grade)
        log(f"Resume graded: ", "OpenAIUtility.grade_resume")
        return response
    
    @classmethod
    def extract_resume_json(self, resume_text: str):
        system_message = """
        Convert the given resume data into a structured JSON format. Adhere strictly to this format:
        {
            "uid": "-1",
            "experience": [{"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "title": "Job Title", "company_name": "Employer Name", description: "Job Description"}, {"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "title": "Job Title", "company_name": "Employer Name", description: "Job Description"}],
            "skills": ["skill1", "skill2"],
            "education": [{"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "course_name": "Degree", "institution": "Institution Name"}, {"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "degree": "course_name", "institution": "Institution Name"}],
        }
        Dates must be formatted as DDMMYYYY or 00000000 if no date is available. if no month or day is available, use 00. for example, if year is 2000 use 00002000.
        Ensure the phone number format includes a hyphen between the country code and the number.
        insure the phones number is total 13 chars with first two country code then hyphen then rest of the number
        uid will always be "-1" for new resumes.
        """
        log("Extracting resume JSON", "OpenAIUtility.extract_resume_json")
        response = self.getResponse(system_message, resume_text, "dict")
        log("Resume JSON extracted", "OpenAIUtility.extract_resume_json")
        return response
    
    @classmethod
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
        log("Extracting job description JSON", "OpenAIUtility.extract_job_description_json")
        response = self.getResponse(system_message, job_description_text, "dict")
        log("Job description JSON extracted", "OpenAIUtility.extract_job_description_json")
        return response


class FileUtility:
    TEMP_DIR = Path("temp_files")
    
    @staticmethod
    def initialize_temp_dir():
        log("Initializing temporary directory", "FileUtility.initialize_temp_dir")
        FileUtility.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        log("Temporary directory initialized", "FileUtility.initialize_temp_dir")

    @staticmethod
    def save_temp_file(file) -> Path:
        log("Saving temporary file", "FileUtility.save_temp_file")
        temp_file_path = FileUtility.TEMP_DIR / file.filename
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        log("Temporary file saved", "FileUtility.save_temp_file")
        return temp_file_path

    @staticmethod
    def extract_text(file_path: Path) -> str:
        log("Extracting text from file", "FileUtility.extract_text")
        if file_path.suffix == '.pdf':
            return FileUtility._extract_text_from_pdf(file_path)
        elif file_path.suffix == '.docx':
            return FileUtility._extract_text_from_docx(file_path)
        else:
            return FileUtility._extract_text_from_txt(file_path)
        

    @staticmethod
    def _extract_text_from_pdf(file_path: Path) -> str:
        log("Extracting text from PDF", "FileUtility._extract_text_from_pdf")
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            log("Text extracted from PDF", "FileUtility._extract_text_from_pdf")
            return ''.join([page.extract_text() for page in reader.pages])

    @staticmethod
    def _extract_text_from_docx(file_path: Path) -> str:
        log("Extracting text from DOCX", "FileUtility._extract_text_from_docx")
        return docx2txt.process(str(file_path))

    @staticmethod
    def _extract_text_from_txt(file_path: Path) -> str:
        with file_path.open("r", encoding='utf-8') as file:
            log("Text extracted from TXT", "FileUtility._extract_text_from_txt")
            return file.read()



if "__main__" == __name__:
    gpt = OpenAIUtility()
    print(gpt.extractIntResponse("I have 20 years of experience but i am not sure if i should work 7.0 more", 0, 10))
