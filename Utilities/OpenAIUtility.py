import openai
import os
from .utility import log, logError
import json
from Processing.DataValidation.GPTOutValidation import JobDescriptionValidation as JDV, ResumeDataValidation as RDV, GradeValidation as GV 


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
        if responseType == "dict" or responseType == "json_str":
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
            if responseType == "dict":
                return response
            elif responseType == "json_str":
                return json.loads(response)
            elif responseType == "str":
                str_response = ""
                for key, value in response:
                    str_response += f"{key}: {value}\n"
                return str_response
            elif responseType == "int":
                probable_response = -1
                for key, value in response:
                    probable_response = int(self.extractNumericResponse(value, min_val, max_val))
                    if probable_response == -1:
                        break
                return probable_response
            elif responseType == "float":
                probable_response = -1.0
                for key, value in response:
                    probable_response = self.extractNumericResponse(value, min_val, max_val)
                    if probable_response == -1.0:
                        break
                return probable_response
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
                return -1.0
        except Exception as e:
            logError("Error extracting int response", e, "OpenAIUtility.extractIntResponse")
            return -1.0

    @classmethod
    def grade_resume(self, job_description: str, resume_data: str, max_grade: int):
        log(f"Grading resume for job description: {job_description}", "OpenAIUtility.grade_resume")
        system_message = f"Grade resumes for this job description: \"{job_description}\" Maximum grade is {max_grade}. " + \
                         "Return -2 if resume is irrelevant to the job description. " + \
                         "Return -1 if job description is not understandable or if the resume data has nothing or is not understandable or enough to make a good judgement. " + \
                         "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Be harsh with your evaluations."
        response = self.getResponse(system_message, resume_data, "int", -2, max_grade)
        validated_response = GV.validate(response, max_grade)
        if not validated_response:
            logError(f"""Grade had a invalid response, defaulting to -1\n
                            INFORMATION:\n
                            JOB-DES: {job_description}
                            RESPONSE: {response}""", "OpenAIUtility.grade_resume")
            return -1
        log(f"Resume graded: ", "OpenAIUtility.grade_resume")
        return response
    
    @classmethod
    def grade_resumes(self, job_description: str, resume_data: dict, max_grade: int):
        log(f"Grading resume for job description: {job_description:<20}", "OpenAIUtility.grade_resume")
        system_message = f"Grade resumes for this job description: \"{job_description}\" Maximum grade is {max_grade}. " + \
                         "Return -2 if resume is irrelevant to the job description. " + \
                         "Return -1 if job description is not understandable or if the resume data has nothing or is not understandable or enough to make a good judgement. " + \
                         "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Be harsh with your evaluations." + \
                         "Output expected is json object with key 'grade' and value a dict with resume number and grade for each resume." + \
                         "example output: {'grade': {'1': '0', '2': '-1', '3': '1', '4': '1', '5': '-2'}} for 5 resumes with max grade 1."
        response = self.getResponse(system_message, "".join([resume + "\nResumeEnd\n" for resume in resume_data]), "dict", -2, max_grade)
        grade_list = []
        for key, value in response["grade"].items():
            grade_list.append(self.extractNumericResponse(value, -2, max_grade))
        clean_grade_list = GV.clean_output(grade_list, max_grade, len(resume_data), response)
        if grade_list != clean_grade_list:
            logError(f"""Grade had a invalid response, defaulting to -1\n
                            INFORMATION:\n
                            JOB-DES: {job_description}
                            RESPONSE: {response}""", "OpenAIUtility.grade_resume")
        log(f"Resumes graded result got response{response} list {grade_list} cleaned {clean_grade_list}", "OpenAIUtility.grade_resume")
        return clean_grade_list
    
    @classmethod
    def extract_resume_json(self, resume_text: str):
        system_message = """
        Convert the given resume data into a structured JSON format. Adhere strictly to this format:
        {
            "uid": "UID",
            "experience": [{"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "title": "Job Title", "company_name": "Employer Name", description: "Job Description"}, {"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "title": "Job Title", "company_name": "Employer Name", description: "Job Description"}],
            "skills": ["skill1", "skill2"],
            "education": [{"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "course_name": "Degree", "institution": "Institution Name"}, {"start_date": "DDMMYYYY", "end_date": "DDMMYYYY", "degree": "course_name", "institution": "Institution Name"}],
        }
        Dates must be formatted as DDMMYYYY or 00000000 if no date is available. if no month or day is available, use 00. for example, if year is 2000 use 00002000.
        Ensure the phone number format includes a hyphen between the country code and the number.
        insure the phones number is total 13 chars with first two country code then hyphen then rest of the number
        uid will always be "UID" for new resumes.
        """
        log("Extracting resume JSON", "OpenAIUtility.extract_resume_json")
        response = self.getResponse(system_message, resume_text, "dict")
        cleaned_response = RDV.clean_output(response)
        if response != cleaned_response:
            logError(f"""Resume had a invalid response, defaulting to -1\n
                            INFORMATION:\n
                            RESPONSE: {response}""", ValueError(), "OpenAIUtility.extract_resume_json")
        log("Resume JSON extracted", "OpenAIUtility.extract_resume_json")
        return cleaned_response
    
    @classmethod
    def extract_job_description_json(self, job_description_text: str):
        system_message = """
        Convert the given job description data into a structured JSON format. Adhere strictly to this format:
        {
            "title": "Job Title",
            "description": "Job Description",
            "company": "Employer Name",
            "required_skills": ["Requirement 1", "Requirement 2"],
            "application_deadline": "DDMMYYYY",
            "location": "Job Location",
            "salary": 0.0,
            "job_type": "FULL",
        }
        job type can be 'FULL', 'PART', 'CONT', or 'UNKN'.
        DEFAULT UNKN
        APPLICATION DATE MUST BE DDMMYYYY FORMAT
        Required skills are skills expected like [	"Product Management", "SQL", "Data Visualization"] these are not experience but skills. experience is in the description
        Ensure that the job description is concise and clearly describes the role, responsibilities, and requirements for the position.
        For must-have requirements, list them only if given in the job description. Must haves are the responsibilities or requirements that are mandatory for the job.
        """
        log("Extracting job description JSON", "OpenAIUtility.extract_job_description_json")
        response = self.getResponse(system_message, job_description_text, "dict")
        response["active"] = True
        cleaned_response = JDV.clean_output(response)
        if response != cleaned_response:
            logError(f"""Job description had a invalid response, defaulting to -1\n
                            INFORMATION:\n
                            RESPONSE: {response}""", ValueError("Error invalid response"), "OpenAIUtility.extract_job_description_json")
        log("Job description JSON extracted", "OpenAIUtility.extract_job_description_json")
        return cleaned_response
