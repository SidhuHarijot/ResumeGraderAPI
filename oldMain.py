#region Imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from mangum import Mangum
from pydantic import BaseModel, Field, model_validator
from openai import OpenAI
import PyPDF2 as pypdf2
import docx2txt
import psycopg2
import psycopg2.pool
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional, Dict
import shutil
from pathlib import Path
#endregion

#region Constants
applicationCodes = {
    100: "Application received",
    101: "Application reviewed",
    200: "Application closed",
    404: "Application not found",
    500: "Internal Server Error",
    501: "Database Error",
    502: "Could not process"
}
#endregion

#region Connection Pool
try:
    # Attempt to connect using the internal URL
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        database="resume_grader",
        user="bugslayerz",
        password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
        host="dpg-coi9t65jm4es739kjul0-a"  # Use your internal URL here
    )
    if connection_pool:
        print("Connection to internal URL successful.")
except (Exception, psycopg2.DatabaseError) as internal_error:
    print("Failed to connect using internal URL:", internal_error)
    
    try:
        # Fallback to the external URL if internal fails
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            database="resume_grader",
            user="bugslayerz",
            password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
            host="dpg-coi9t65jm4es739kjul0-a.oregon-postgres.render.com"  # External URL
        )
        if connection_pool:
            print("Connection to external URL successful.")
    except (Exception, psycopg2.DatabaseError) as external_error:
        print("Failed to connect using external URL:", external_error)
#endregion

#region Fast API Initialization
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://localhost",
    "http://localhost:3006",
    "https://client-resume-upload-p9g0bmvaf-harijot-singhs-projects.vercel.app",
    "https://client-resume-upload.vercel.app",
    "https://client-resume-upload-git-master-harijot-singhs-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

@app.get("/")
def read_root():
    return {"version": "2.0",
            "author": "Harijot Singh, Yuvraj Singh Chohan",
            "Title": "Resume Grader",
            "Description": "This is an API to grade resumes for a provided job description."}

#endregion

#region Pydantic Models
class GradeRequestData(BaseModel):
    resumeData: Dict[int, str] = Field(..., description="Mapping of resume IDs to their respective data.")
    jobDescription: str = Field(..., description="Description of the job for which resumes are being graded.")
    noOfResumes: int = Field(..., description="Expected number of resumes to be provided.")
    apiKey: str = Field(..., description="API key for authentication.")

    @model_validator(mode="after")
    def checkResumeCount(self):
        if len(self.resumeData) != self.noOfResumes:
            raise ValueError("Number of resumes does not match the number of resume data provided.")
        return self


class Experience(BaseModel):
    start_date: str = Field(..., description="Start date of the experience. format: DDMMYYYY example: 01011999")
    end_date: str = Field(..., description="End date of the experience. format: DDMMYYYY example: 01011999")
    title: str = Field(..., description="Title of the experience.")
    company_name: str = Field(..., description="Name of the company.")
    description: str = Field(..., description="Description of the experience.")
    
    def format_to_string(self):
        return f"+{{{self.start_date}}}-{{{self.end_date}}}: {self.title} at {self.company_name} - {self.description}"

class Education(BaseModel):
    start_date: str = Field(..., description="Start date of the education. format: DDMMYYYY example: 01011999")
    end_date: str = Field(..., description="End date of the education. format: DDMMYYYY example: 01011999")
    institution: str = Field(..., description="Name of the institution.")
    course_name: str = Field(..., description="Name of the course.")

class ExtractRequestData(BaseModel):
    stringData: str = Field(..., description="String data to be extracted.")
    apiKey: str = Field(..., description="API key for authentication.")

class Resume(BaseModel):
    uid: str = Field(..., description="User ID associated with the resume.")
    skills: List[str] = Field(..., description="List of skills")
    experience: List[Experience] = Field(..., description="List of experiences")
    education: List[Education] = Field(..., description="List of educations")

class Job(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    title: str = Field(..., description="Title of the job.")
    company: str = Field(..., description="Company name.")
    description: str = Field(..., description="Description of the job.")
    required_skills: str = Field(..., description="Required skills for the job.")
    application_deadline: str = Field(..., description="Deadline for job applications.")
    location: str = Field(..., description="Location of the job.")
    salary: float = Field(..., description="Salary for the job.")
    highly_preferred_skills: List[str] = Field(..., description="List of highly preferred skills.")
    active: bool = Field(..., description="Status of the job, whether it is active or not.")

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the job application.")
    uid: str = Field(..., description="User ID associated with the resume used in the application.")
    job_id: int = Field(..., description="Unique identifier of the job applied for.")
    match_percentage: Optional[float] = Field(None, description="Match percentage between resume and job.")
    status: str = Field(None, description="Status of the match.")
    status_code: float = Field(None, description="status code of the match.")
    grade: int = Field(None, description="Grade assigned to the resume.")

class ResumeWithGrade(BaseModel):
    uid: str = Field(..., description="User ID associated with the resume.")
    resume_data: Dict = Field(..., description="Data of the resume.")
    grade: Optional[int] = Field(None, description="Optional grade assigned to the resume.")

class GradingRequest(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    uid: str = Field(..., description="User ID associated with the resume.")
    apiKey: str = Field(..., description="API key for authentication.")
    maxGrade: int = Field(default=1, description="Maximum grade that can be assigned.")

class Profile(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    name: str = Field(..., description="Name of the user.")
    dob: str = Field(..., description="Date of birth of the user. format: DDMMYYYY example: 01011999")
    is_owner: bool = Field(..., description="Status of the user, whether they are the owner or not.")
    is_admin: bool = Field(..., description="Status of the user, whether they are an admin or not.")
    resume_data: Optional[Resume] = Field(None, description="Data of the resume.")
    phone_number: str = Field(..., description="Phone number of the user.")
    email: str = Field(..., description="Email of the user.")

class User(BaseModel):
    name: str = Field(..., description="Name of the user.")
    dob: str = Field(..., description="Date of birth of the user. format: DDMMYYYY example: 01011999")
    uid: str = Field(..., description="Unique identifier for the user.")
    is_owner: bool = Field(..., description="Status of the user, whether they are the owner or not.")
    is_admin: bool = Field(..., description="Status of the user, whether they are an admin or not.")
    phone_number: str = Field(..., description="Phone number of the user.")
    email: str = Field(..., description="Email of the user.")


#endregion

#region Grading Endpoints
@app.post("/grade/ChatGPT/", response_model=Match)
async def grade_resume(request: GradingRequest):
    """
    Grade a specific resume for a job.

    Args:
        request (GradingRequest): Request object containing job_id, uid, apiKey, and maxGrade.
        Example:
        {
            "job_id": 1,
            "uid": "1234567890",
            "apiKey": "sk-XXXXXXXX",
            "maxGrade": 1
        }

    Returns:
        Match: Match object containing the uid, job_id, and grade.
        Example:
        {
            "match_id": 1,
            "uid": "1234567890",
            "job_id": 1,
            "grade": 1
        }
    
    Raises:
        HTTPException: If an error occurs during grading.
    """
    if not request.uid:
        raise HTTPException(status_code=400, detail="Invalid UID")
    grade = await _grade_resume_chatGPT(request.apiKey, request.job_id, [request.uid], request.maxGrade)
    grade = grade[request.uid]
    result = await save_match(request.uid, request.job_id, grade)
    return result

async def save_match(uid: str, job_id: int, grade: int):
    """
    Save the match data to the database.

    Args:
        uid (str): Unique identifier for the user.
        job_id (int): Unique identifier for the job.
        grade (int): Grade assigned to the resume.

    Returns:
        Match: Match object containing the uid, job_id, and grade.
        Example:
        {
            "match_id": 1,
            "uid": "1234567890",
            "job_id": 1,
            "grade": 1
        }
    
    Raises:
        HTTPException: If an error occurs during saving.
    """
    logAPI(f"Saving match for user {uid} and job {job_id}", "save_match", "INFO")
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO matches (uid, job_id, grade)
                VALUES (%s, %s, %s)
                ON CONFLICT (uid, job_id) DO UPDATE SET grade = EXCLUDED.grade
            """, (uid, job_id, grade))
            con.commit()
            logSQL(f"Match for user {uid} and job {job_id} saved successfully", "save_match")
        return Match(uid=uid, job_id=job_id, grade=grade)
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "save_match", "ERROR")
        raise HTTPException(status_code=500, detail=f"Failed to save match: {str(e)}")
    finally:
        if con:
            connection_pool.putconn(con)

async def _grade_resume_chatGPT(api_key, job_id: int, uids: List[str], max_grade: int):
    """
    Grade resumes using ChatGPT.

    Args:
        api_key (str): OpenAI API key.
        job_id (int): Unique identifier for the job.
        uids (List[str]): List of user IDs to be graded.
        max_grade (int): Maximum grade that can be assigned.

    Returns:
        Dict[str, int]: Dictionary mapping user IDs to their grades.
        Example:
        {
            "1234567890": 1,
            "0987654321": 0
        }
    
    Raises:
        Exception: If an error occurs during grading.
    """
    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")
    grades = {}

    job_description = str(get_job(job_id))
    resume_list = [get_resume(uid) for uid in uids]

    system_string = f"Grade resumes for this job description: \"{job_description}\" Maximum grade is {max_grade}. " + \
                   "Just answer in the number or the grade nothing else. " + \
                   "Return -2 if resume is irrelevant to the job description" + \
                   "Return -1 if job description is not understandable or if the resume data has nothing or not understandable or enough to make good judgement." + \
                   "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Also be harsh with your evaluations"

    messages = [{"role": "system", "content": system_string}]

    for resume in resume_list:
        individual_messages = messages.copy()  # Copy the base messages list
        individual_messages.append({"role": "user", "content": str(resume)})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=individual_messages
            )
            # Assuming each response contains a number directly (you may need to parse or process text)
            last_message = response.choices[0].message.content.strip()
            if int(last_message) == -1:
                grades[resume.uid] = -1
            else:
                grades[resume.uid] = int(last_message)
        except Exception as e:
            grades[resume.uid] = -1

    return grades

@app.post("/grade/ChatGPT/job/{job_id}")
async def grade_all_from_job(request: GradingRequest):
    """
    Grade all resumes for a specific job.

    Args:
        request (GradingRequest): Request object containing job_id, apiKey, and maxGrade.
        Example:
        {
            "job_id": 1,
            "apiKey": "sk-XXXXXXXX",
            "maxGrade": 1
        }

    Returns:
        dict: Dictionary containing the status and grades.
        Example:
        {
            "status": "Application reviewed",
            "status_code": 100,
            "grades": {
                "1234567890": 1,
                "0987654321": 0
            }
        }
    
    Raises:
        HTTPException: If an error occurs during grading.
    """
    logAPI(f"Grading all resumes for job {request.job_id}", "grade_all_from_job", "INFO")
    status_code = 502
    status = "Error Unknown"
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT uid FROM matches WHERE job_id = %s", (request.job_id,))
            uids = cursor.fetchall()
            cursor.execute("SELECT job_data FROM jobdescriptions WHERE job_id = %s", (request.job_id,))
            job_data = cursor.fetchone()
            if job_data:
                grades = await _grade_resume_chatGPT(request.apiKey, request.job_id, uids, request.maxGrade)
                for uid, grade in grades.items():
                    cursor.execute("""
                        INSERT INTO matches (uid, job_id, grade)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (uid, job_id) DO UPDATE SET grade = EXCLUDED.grade
                    """, (uid, request.job_id, grade))
                con.commit()
                status_code = 100
                status = ""
                logSQL(f"All resumes for job {request.job_id} graded successfully", "grade_all_from_job")
            else:
                status_code = 404
                status = "Job not found"
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "grade_all_from_job", "ERROR")
        con.rollback()
        status_code = 500
    finally:
        if con:
            connection_pool.putconn(con)
    return {"status": applicationCodes[status_code] + status, "status_code": status_code, "grades": grades}
#endregion

#region Extracting Endpoints
@app.post("/extract/resumeJSON/ChatGPT")
def extract_resume_json(request_data: ExtractRequestData):
    """
    Extract resume data into JSON format using ChatGPT.

    Args:
        request_data (ExtractRequestData): Request object containing stringData and apiKey.
        Example:
        {
            "stringData": "Resume data...",
            "apiKey": "sk-XXXXXXXX"
        }

    Returns:
        dict: Dictionary containing the extracted resume data.
        Example:
        {
            "name": ["FirstName", "LastName"],
            "experience": [{"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}, {"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}],
            "skills": ["skill1", "skill2"],
            "education": [{"DDMMYYYY-DDMMYYYY": {"INSTITUTION": "COURSE NAME"}}]
        }
    
    Raises:
        Exception: If an error occurs during extraction.
    """
    client = OpenAI(api_key=request_data.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    system_string = """
    Convert the given resume data into a structured JSON format. Adhere strictly to this format: 
    {
        "name": ["FirstName", "LastName"],
        "experience": [{"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}, {"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}],
        "skills": ["skill1", "skill2"],
        "education": [{"DDMMYYYY-DDMMYYYY": {"INSTITUTION": "COURSE NAME"}}],
    }
    Dates must be formatted as DDMMYYYY or 00000000 if no date is available.
    Ensure the phone number format includes a hyphen between the country code and the number. 
    It is critical that you follow the format precisely as described to ensure the data can be parsed correctly by the program without errors.
    """ 
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_string},
            {"role": "user", "content": request_data.stringData}
        ],
        response_format={"type": "json_object"}
    )
    print(type(response.choices[0].message.content))
    print(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)

@app.post("/extract/resume")
async def extract_resume(api_key: str, uid: str, file: UploadFile = File(...)):
    """
    Extracts resume data from the provided file and returns a Profile object with the extracted data.

    Args:
        api_key (str): OpenAI API key.
        uid (str): User ID.
        file (UploadFile): File containing the resume data.
        Example:
        {
            "apiKey": "sk-XXXXXXXX",
            "uid": "1234567890",
            "file": <file>
        }
        
    Returns:
        Profile: Profile object containing the extracted resume data.
        Example:
        {
            "skills": ["skill1", "skill2"],
            "experience": [{"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}, {"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}],
            "education": [{"DDMMYYYY-DDMMYYYY": {"INSTITUTION": "COURSE NAME"}}]
        }
    
    Raises:
        HTTPException: If an error occurs during the extraction process.
    """
    logAPI(f"Extracting resume for user {uid}", "extract_resume", "INFO")
    try:
        temp_file_path = await save_temp_file(file)
        resume_text = await extract_text(temp_file_path)
        data = ExtractRequestData(stringData=resume_text, apiKey=api_key)
        resume_json = extract_resume_json(data)
        temp_file_path.unlink()
        logAPI(f"Resume extracted for user {uid} result {resume_json}", "extract_resume", "INFO")
        logAPI(f"Resume extracted for user {uid} result type {type(resume_json)}", "extract_resume", "INFO")
        resume = Resume(
            uid=uid,
            skills=resume_json["skills"],
            experience=resume_json["experience"],
            education=resume_json["education"]
        ) 
    except Exception as e:
        logAPI(f"An error occurred: {e}", "extract_resume", "ERROR")
        raise e
        raise HTTPException(status_code=500, detail=f"Failed to extract resume data: {str(e)}")
    return resume

@app.post("/extract/jobDescriptionJSON/ChatGPT")
def extract_job_description_json(request_data: ExtractRequestData):
    """
    Extract job description data into JSON format using ChatGPT.

    Args:
        request_data (ExtractRequestData): Request object containing stringData and apiKey.
        Example:
        {
            "stringData": "Job description data...",
            "apiKey": "sk-XXXXXXXX"
        }

    Returns:
        dict: Dictionary containing the extracted job description data.
        Example:
        {
            "Title": "Job Title",
            "description": "Job Description",
            "employer": "Employer Name",
            "Must Haves": ["Requirement 1", "Requirement 2"]
        }
    
    Raises:
        Exception: If an error occurs during extraction.
    """
    client = OpenAI(api_key=request_data.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    system_string = """
    Convert the given job description data into a structured JSON format. Adhere strictly to this format: 
    {
        "Title": "Job Title",
        "description": "Job Description",
        "employer": "Employer Name",
        "Must Haves": ["Requirement 1", "Requirement 2"]
    }
    Ensure that the job description is concise and clearly describes the role, responsibilities, and requirements for the position.
    For must have requirements, list them only if given in the job description. Must haves are the responsibilities or requirements that are mandatory for the job.
    """ 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_string},
            {"role": "user", "content": request_data.stringData}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].text)
#endregion

#region checkPermission Endpoints
def check_is_admin(uid: str):
    """
    Check if the user is an admin.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        bool: True if the user is an admin, False otherwise.
    
    Raises:
        Exception: If an error occurs during the check.
    """
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE uid = %s", (uid,))
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "check_is_admin", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return False

def check_is_owner(uid: str):
    """
    Check if the user is the owner.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        bool: True if the user is the owner, False otherwise.
    
    Raises:
        Exception: If an error occurs during the check.
    """
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT is_owner FROM users WHERE uid = %s", (uid,))
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "check_is_owner", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return False

def checkEmailInUse(email: str):
    """
    Check if the email is already in use.

    Args:
        email (str): Email ID.
        Example:
        {
            "email": "something@some.com"
        }

    Returns:
        bool: True if the email is in use, False otherwise.

    Raises:
        Exception: If an error occurs during the check.
    """
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            return cursor.fetchone() is not None
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "checkEmailInUse", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return False
#endregion

#region Upload Endpoints
@app.post("/upload/resume/")
async def upload_resume(api_key: str, uid: str, file: UploadFile = File(...)):
    """
    Upload a resume file and save the extracted data.

    Args:
        api_key (str): OpenAI API key.
        uid (str): User ID.
        file (UploadFile): File containing the resume data.
        Example:
        {
            "apiKey": "sk-XXXXXXXX",
            "uid": "1234567890",
            "file": <file>
        }

    Returns:
        dict: Dictionary containing the status and uid.
        Example:
        {
            "status": "Resume uploaded successfully",
            "uid": "1234567890"
        }
    
    Raises:
        HTTPException: If an error occurs during the upload.
    """
    logAPI(f"Uploading resume for user {uid}", "upload_resume", "INFO")
    try:
        temp_file_path = await save_temp_file(file)
        resume_text = await extract_text(temp_file_path)
        data = ExtractRequestData(stringData=resume_text, apiKey=api_key)
        resume_json = extract_resume_json(data)
        temp_file_path.unlink()
        resume = Resume(
            uid=uid,
            skills=resume_json["skills"],
            experience=resume_json["experience"],
            education=resume_json["education"]
        )
        return await save_resume_data(resume)
    except Exception as e:
        logAPI(f"An error occurred: {e}", "upload_resume", "ERROR")
        raise HTTPException(status_code=500, detail=f"Failed to extract resume data: {str(e)}")

@app.post("/upload/job/file")
async def upload_job(api_key: str, file: UploadFile = File(...)):
    """
    Upload a job description file and save the extracted data.

    Args:
        api_key (str): OpenAI API key.
        file (UploadFile): File containing the job description data.
        Example:
        {
            "apiKey": "sk-XXXXXXXX",
            "file": <file>
        }

    Returns:
        dict: Dictionary containing the status and job_id.
        Example:
        {
            "status": "Job uploaded successfully",
            "job_id": 1
        }
    
    Raises:
        HTTPException: If an error occurs during the upload.
    """
    logAPI("Uploading job description", "upload_job", "INFO")
    try:

        temp_file_path = await save_temp_file(file)
        job_text = await extract_text(temp_file_path)
        job_json = extract_job_description_json(ExtractRequestData(stringData=job_text, apiKey=api_key))
        temp_file_path.unlink()
        return await save_job_data(job_json)
    except Exception as e:
        logAPI(f"An error occurred: {e}", "upload_job", "ERROR")
        raise HTTPException(status_code=500, detail=f"Failed to extract job data: {str(e)}")

@app.post("/upload/job")
def upload_job_data(job_data: Job):
    """
    Upload job description data to the database.

    Args:
        job_data (Job): Job description data to be uploaded.
        Example:
        {
            "job_id": 1,
            "title": "Job Title",
            "company": "Company Name",
            "description": "Job Description",
            "required_skills": "Skills",
            "application_deadline": "2024-12-31",
            "location": "Location",
            "salary": 100000.00,
            "highly_preferred_skills": ["skill1", "skill2"],
        }

    Returns:
        dict: Dictionary containing the status and job_id.
        Example:
        {
            "status": "Job uploaded successfully",
            "job_id": 1
        }

    Raises:
        HTTPException: If an error occurs during the upload.
    """
    logAPI(f"Uploading job {job_data.title} at {job_data.company}", "upload_job_data", "INFO")
    return save_job_data(job_data)

async def save_temp_file(file: UploadFile):
    """
    Save the uploaded file temporarily.

    Args:
        file (UploadFile): File to be saved.
        Example:
        {
            "file": <file>
        }

    Returns:
        Path: Path to the saved temporary file.
    
    Raises:
        Exception: If an error occurs during saving.
    """
    temp_file_path = Path(f"temp_files/{file.filename}")
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_file_path

async def extract_text(file_path: Path):
    """
    Extract text from the provided file.

    Args:
        file_path (Path): Path to the file.
        Example:
        {
            "file_path": "temp_files/resume.pdf"
        }

    Returns:
        str: Extracted text from the file.
    
    Raises:
        Exception: If an error occurs during extraction.
    """
    if file_path.suffix == '.pdf':
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf2.PdfReader(file)
            content = pdf_reader.pages[0].extract_text() if pdf_reader.pages else ""
    elif file_path.suffix == '.docx':
        content = docx2txt.process(str(file_path))
    else:
        with file_path.open("r", encoding='utf-8') as file:
            content = file.read()
    return content

def save_resume_data(resume_data: Resume):
    """
    Save the extracted resume data to the database.

    Args:
        resume_data (Resume): Extracted resume data.
        Example:
        {
            "uid": "1234567890",
            "skills": ["skill1", "skill2"],
            "experience": ["experience1", "experience2"],
            "education": ["education1", "education2"]
        }

    Returns:
        dict: Dictionary containing the status and uid.
        Example:
        {
            "status": "Resume uploaded successfully",
            "uid": "1234567890"
        }
    
    Raises:
        HTTPException: If an error occurs during saving.
    """
    logAPI(f"Saving resume for user {resume_data.uid}", "save_resume_data", "INFO")
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO resumes (uid, skills, experience, education) VALUES (%s, %s, %s, %s)", 
                           (resume_data.uid, json.dumps(resume_data.skills), json.dumps(resume_data.experience), json.dumps(resume_data.education)))
            con.commit()
            logSQL(f"Resume for user {resume_data.uid} saved successfully", "save_resume_data")
        return {"status": "Resume uploaded successfully", "uid": resume_data.uid}
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "save_resume_data", "ERROR")
        raise HTTPException(status_code=500, detail=f"Failed to upload resume, error: {str(e)}")
    finally:
        if con:
            connection_pool.putconn(con)

def save_job_data(job_data: Job):
    """
    Save the extracted job description data to the database.

    Args:
        job_data (Job): Extracted job description data.
        Example:
        {
            "title": "Job Title",
            "company": "Company Name",
            "description": "Job Description",
            "required_skills": "Skills",
            "application_deadline": "2024-12-31",
            "location": "Location",
            "salary": 100000.00,
            "highly_preferred_skills": ["skill1", "skill2"],
        }

    Returns:
        dict: Dictionary containing the status and job_id.
        Example:
        {
            "status": "Job uploaded successfully",
            "job_id": 1
        }
    
    Raises:
        HTTPException: If an error occurs during saving.
    """
    logAPI(f"Saving job {job_data.title} at {job_data.company}", "save_job_data", "INFO")
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobdescriptions (
                    title, company, description, required_skills, application_deadline, 
                    location, salary, highly_preferred_skills, active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s::text[], %s
                ) RETURNING job_id
            """, (
                job_data.title, job_data.company, job_data.description, job_data.required_skills, 
                job_data.application_deadline, job_data.location, job_data.salary, 
                job_data.highly_preferred_skills, job_data.active
            ))
            job_id = cursor.fetchone()[0]
            con.commit()
            logSQL(f"Job {job_data.title} saved successfully with job_id {job_id}", "save_job_data")
        return {"status": "Job uploaded successfully", "job_id": job_id}
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "save_job_data", "ERROR")
        return {"status": "Failed to upload job", "error": str(e)}
    finally:
        if con:
            connection_pool.putconn(con)

@app.post("/upload/application")
def upload_application(data: Match):
    """
    Upload an application (match) to the database.

    Args:
        data (Match): Match data to be uploaded.
        Example:
        {
            "uid": "1234567890",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 0
        }

    Returns:
        dict: Dictionary containing the status and match_id.
        Example:
        {
            "status": "Application received",
            "status_code": 100,
            "match_id": 1
        }
    
    Raises:
        HTTPException: If an error occurs during the upload.
    """
    logAPI(f"Uploading application for user {data.uid} to job {data.job_id}", "upload_application", "INFO")
    status_code = 502
    status = "Error Unknown"
    match_id = -1
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO matches (uid, job_id, status, status_code, grade) VALUES (%s, %s, %s, %s, %s) RETURNING match_id", 
                           (data.uid, data.job_id, data.status, data.status_code, data.grade))
            match_id = cursor.fetchone()[0]
            con.commit()
            logSQL(f"Application for user {data.uid} to job {data.job_id} uploaded successfully", "upload_application")
        status_code = 100
        status = ""
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "upload_application", "ERROR")
        con.rollback()
        status_code = 500
    finally:
        if con:
            connection_pool.putconn(con)
    return {"status": applicationCodes[status_code] + status, "status_code": status_code, "match_id": match_id}

@app.post("/upload/user")
def upload_user(data: User):
    """
    Upload user data to the database.

    Args:
        data (User): User data to be uploaded.
        Example:
        {
            "name": "John Doe",
            "dob": "01011999",
            "uid": "1234567890",
            "is_owner": false,
            "is_admin": false,
            "phone_number": "+XX-XXXXXXXXXX",
            "email": "john.doe@example.com"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "User uploaded successfully",
            "status_code": 100
        }
    
    Raises:
        HTTPException: If an error occurs during the upload process.
    """
    logAPI(f"Uploading user {data.uid}", "upload_user", "INFO")
    status_code = 502
    status = "Error Unknown"
    try:
        data.is_owner = False
        data.is_admin = False
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (uid, name, dob, is_owner, is_admin, phone_number, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (uid) DO UPDATE SET name = EXCLUDED.name, dob = EXCLUDED.dob, is_owner = EXCLUDED.is_owner, is_admin = EXCLUDED.is_admin, phone_number = EXCLUDED.phone_number, email = EXCLUDED.email
            """, (data.uid, data.name, data.dob, data.is_owner, data.is_admin, data.phone_number, data.email))
            con.commit()
            logSQL(f"User {data.uid} uploaded successfully", "upload_user")
            status_code = 100
            status = ""
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "upload_user", "ERROR")
        con.rollback()
        status_code = 500
        raise HTTPException(status_code=500, detail=f"Failed to upload user: {str(e)}")
    finally:
        if con:
            connection_pool.putconn(con)
    return {"status": applicationCodes[status_code] + status, "status_code": status_code}
#endregion

#region SQL Endpoints
@app.get("/createTables")
def create_tables():
    """
    Create the necessary tables in the database.

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Tables created successfully",
            "status_code": 200
        }
    
    Raises:
        HTTPException: If an error occurs during the table creation process.
    """
    logAPI("Creating tables", "create_tables", "INFO")
    sql_error = ""
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
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
                        resume_id SERIAL PRIMARY KEY,
                        uid VARCHAR(50) NOT NULL,
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
                        job_type VARCHAR(100) CHECK (job_type IN ('FULL', 'PART', 'CONT', 'UNKN')),
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
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            for table_name, table_schema in tables.items():
                cursor.execute(table_schema)
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
            logAPI("Tables Updated Successfully", "createTables", "INFO")
            logAPI("Creating INDEXES", "createTables", "INFO")
            for table_name, index_schema in indexes.items():
                cursor.execute(index_schema)
            con.commit() 
            logSQL("INDEXES Updated Successfully", "createTables")
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "create_tables", "ERROR")
        con.rollback()
        sql_error = str(e)
    finally:
        if con:
            connection_pool.putconn(con)

    if sql_error:
        return {"status": "An error occurred while creating tables", "sql_error": sql_error, "status_code": 500}
    else:
        return {"status": "Tables created successfully", "status_code": 200}
#endregion

#region Retrieve Endpoints
@app.get("/retrieve/resume/{uid}", response_model=Resume)
def get_resume(uid: str):
    """
    Retrieve a resume by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        Resume: Resume object containing the resume data.
        Example:
        {
            "uid": "1234567890",
            "skills": ["skill1", "skill2"],
            "experience": ["experience1", "experience2"],
            "education": ["education1", "education2"]
        }
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    resume = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM resumes WHERE uid = %s", (uid,))
            resume = cursor.fetchone()
            if resume:
                resume_data = json.loads(resume[2])
                resume = Resume(uid=resume[1], skills=resume_data['skills'], experience=resume_data['experience'], education=resume_data['education'])
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_resume", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return resume

@app.get("/retrieve/job/{job_id}", response_model=Job)
def get_job(job_id: int):
    """
    Retrieve a job by job ID.

    Args:
        job_id (int): Job ID.
        Example:
        {
            "job_id": 1
        }

    Returns:
        Job: Job object containing the job data.
        Example:
        {
            "job_id": 1,
            "job_data": {
                "title": "Job Title",
                "company": "Company Name",
                "description": "Job Description",
                "required_skills": "Skills",
                "application_deadline": "2024-12-31",
                "location": "Location",
                "salary": 100000.00,
                "highly_preferred_skills": ["skill1", "skill2"]
            },
            "active": true
        }
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    job = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM jobdescriptions WHERE job_id = %s", (job_id,))
            job = cursor.fetchone()
            if job:
                job = Job(job_id=job[0], title=job[1], company=job[2], description=job[3], required_skills=job[4], application_deadline=job[5], location=job[6], salary=job[7], highly_preferred_skills=job[8], active=job[9])
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_job", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return job

@app.get("/retrieve/match/{match_id}", response_model=Match)
def get_match(match_id: int):
    """
    Retrieve a match by match ID.

    Args:
        match_id (int): Match ID.
        Example:
        {
            "match_id": 1
        }

    Returns:
        Match: Match object containing the match data.
        Example:
        {
            "match_id": 1,
            "uid": "1234567890",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 1
        }
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    match = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM matches WHERE match_id = %s", (match_id,))
            match = cursor.fetchone()
            if match:
                match = Match(match_id=match[0], uid=match[1], job_id=match[2], status=match[4], status_code=match[5], grade=match[6])
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_match", "ERROR")
    finally:
        if con:
            connection_pool.putconn(con)
    return match

@app.get("/retrieve/resumes/", response_model=List[Resume])
async def get_resumes(uid: Optional[str] = None):
    """
    Retrieve all resumes or a specific resume by UID.

    Args:
        uid (Optional[str]): User ID (optional).
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        List[Resume]: List of Resume objects containing the resume data.
        Example:
        [
            {
                "uid": "1234567890",
                "skills": ["skill1", "skill2"],
                "experience": ["experience1", "experience2"],
                "education": ["education1", "education2"]
            },
            {
                "uid": "0987654321",
                "skills": ["skill3", "skill4"],
                "experience": ["experience3", "experience4"],
                "education": ["education3", "education4"]
            }
        ]
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving resumes, uid: {uid}", "get_resumes", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            if uid:
                cursor.execute("SELECT * FROM resumes WHERE uid = %s", (uid,))
            else:
                cursor.execute("SELECT * FROM resumes")
            results = cursor.fetchall()
            return [Resume(uid=resume[1], skills=json.loads(resume[2])['skills'], experience=json.loads(resume[2])['experience'], education=json.loads(resume[2])['education']) for resume in results]
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_resumes", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.get("/retrieve/jobs/", response_model=List[Job])
async def get_jobs(active: Optional[bool] = None):
    """
    Retrieve all jobs or active/inactive jobs.

    Args:
        active (Optional[bool]): Filter for active jobs (optional).
        Example:
        {
            "active": true
        }

    Returns:
        List[Job]: List of Job objects containing the job data.
        Example:
        [
            {
                "job_id": 1,
                "title": "Job Title",
                "company": "Company Name",
                "description": "Job Description",
                "required_skills": "Skills",
                "application_deadline": "2024-12-31",
                "location": "Location",
                "salary": 100000.00,
                "highly_preferred_skills": ["skill1", "skill2"],
                "active": true
            },
            {
                "job_id": 2,
                "title": "Another Job Title",
                "company": "Another Company",
                "description": "Another Job Description",
                "required_skills": "More Skills",
                "application_deadline": "2024-12-31",
                "location": "Another Location",
                "salary": 120000.00,
                "highly_preferred_skills": ["skill5", "skill6"],
                "active": false
            }
        ]
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving jobs, active: {active}", "get_jobs", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            if active is not None:
                cursor.execute("SELECT * FROM jobdescriptions WHERE active = %s", (active,))
            else:
                cursor.execute("SELECT * FROM jobdescriptions")
            results = cursor.fetchall()
            
            return [Job(job_id=job[0],
                title=job[1],
                company=job[2],
                description=job[3],
                required_skills=job[4],
                application_deadline=job[5],
                location=job[6],
                salary=job[7],
                highly_preferred_skills=job[8],
                active=job[9]) for job in results]
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_jobs", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.get("/retrieve/resumes_with_grades/", response_model=List[ResumeWithGrade])
async def get_resumes_with_grades(job_id: int):
    """
    Retrieve resumes with grades for a specific job.

    Args:
        job_id (int): Job ID.
        Example:
        {
            "job_id": 1
        }

    Returns:
        List[ResumeWithGrade]: List of ResumeWithGrade objects containing the resume data and grades.
        Example:
        [
            {
                "uid": "1234567890",
                "resume_data": {
                    "skills": ["skill1", "skill2"],
                    "experience": ["experience1", "experience2"],
                    "education": ["education1", "education2"]
                },
                "grade": 1
            },
            {
                "uid": "0987654321",
                "resume_data": {
                    "skills": ["skill3", "skill4"],
                    "experience": ["experience3", "experience4"],
                    "education": ["education3", "education4"]
                },
                "grade": 0
            }
        ]
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving resumes with grades for job {job_id}", "get_resumes_with_grades", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            query = """
            SELECT r.uid, r.skills, r.experience, r.education, m.grade
            FROM resumes r
            LEFT JOIN matches m ON r.uid = m.uid AND m.job_id = %s
            WHERE EXISTS (
                SELECT 1 FROM matches WHERE job_id = %s AND uid = r.uid
            )
            """
            cursor.execute(query, (job_id, job_id))
            results = cursor.fetchall()
            return [ResumeWithGrade(uid=resume[0], resume_data={"skills": json.loads(resume[1])['skills'], "experience": json.loads(resume[1])['experience'], "education": json.loads(resume[1])['education']}, grade=resume[4]) for resume in results]
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_resumes_with_grades", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.get("/retrieve/user/{uid}", response_model=User)
async def get_user(uid: str):
    """
    Retrieve a user by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        User: User object containing the user data.
        Example:
        {
            "name": "John Doe",
            "dob": "01011999",
            "uid": "1234567890",
            "is_owner": false,
            "is_admin": false,
            "phone_number": "+XX-XXXXXXXXXX",
            "email": "john.doe@example.com"
        }
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving user {uid}", "get_user", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if user:
                return User(
                    name=user[1],
                    dob=user[2],
                    uid=user[0],
                    is_owner=user[3],
                    is_admin=user[4],
                    phone_number=user[5],
                    email=user[6]
                )
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_user", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.get("/retrieve/profile/{uid}", response_model=Profile)
async def get_profile(uid: str):
    """
    Retrieve the profile of a user.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        Profile: Profile object containing the user's data.
        Example:
        {
            "uid": "1234567890",
            "name": "John Doe",
            "dob": "01011999",
            "is_owner": false,
            "is_admin": false,
            "resume_data": {
                "skills": ["skill1", "skill2"],
                "experience": ["experience1", "experience2"],
                "education": ["education1", "education2"]
            },
            "phone_number": "+XX-XXXXXXXXXX",
            "email": "john.doe@example.com"
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving profile for user {uid}", "get_profile", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if user:
                resume = get_resume(uid)
                return Profile(
                    uid=user[0],
                    name=user[1],
                    dob=user[2],
                    is_owner=user[3],
                    is_admin=user[4],
                    resume_data=resume,
                    phone_number=user[5],
                    email=user[6]
                )
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_profile", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)


@app.get("/retrieve/role/{uid}")
def get_user_role(uid: str):
    """
    Retrieve the role of a user.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        dict: Dictionary containing the role of the user.
        Example:
        {
            "role": "Owner",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    logAPI(f"Retrieving role for user {uid}", "get_user_role", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT is_owner, is_admin FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if user:
                if user[0]:
                    return {"role": "Owner", "status_code": 100}
                elif user[1]:
                    return {"role": "Admin", "status_code": 100}
                else:
                    return {"role": "User", "status_code": 100}
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "get_user_role", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)
#endregion

#region Update Endpoints
@app.put("/update/user/makeAdmin/{uid}")
async def make_user_admin(uid: str, owner_uid: str):
    """
    Make a user an admin.

    Args:
        uid (str): User ID.
        owner_uid (str): Owner user ID.
        Example:
        {
            "uid": "1234567890",
            "owner_uid": "0987654321"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "User updated successfully",
            "status_code": 100
        }
    
    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logAPI(f"Making user {uid} an admin by owner {owner_uid}", "make_user_admin", "INFO")
    con = connection_pool.getconn()
    try:
        if not check_is_owner(owner_uid):
            raise HTTPException(status_code=403, detail="You do not have permission to make this user an admin.")
        with con.cursor() as cursor:
            cursor.execute("UPDATE users SET is_admin = TRUE WHERE uid = %s", (uid,))
            con.commit()
            logSQL(f"User {uid} made admin successfully", "make_user_admin")
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "make_user_admin", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.put("/update/job/{job_id}")
async def update_job(job_id: int, job_data: dict):
    """
    Update a job description.

    Args:
        job_id (int): Job ID.
        job_data (dict): Job data to be updated.
        Example:
        {
            "job_id": 1,
            "job_data": {
                "title": "Updated Job Title",
                "company": "Updated Company",
                "description": "Updated Job Description",
                "required_skills": "Updated Skills",
                "application_deadline": "2025-01-01",
                "location": "Updated Location",
                "salary": 120000.00,
                "highly_preferred_skills": ["updated_skill1", "updated_skill2"],
                active: true
            }
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Job updated successfully",
            "status_code": 100
        }
    
    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logAPI(f"Updating job {job_id}", "update_job", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("UPDATE jobdescriptions SET title = %s, company = %s, description = %s, required_skills = %s, application_deadline = %s, location = %s, salary = %s, highly_preferred_skills = %s, active = %s WHERE job_id = %s".format(
                job_data["title"], job_data["company"], job_data["description"], job_data["required_skills"], job_data["application_deadline"], job_data["location"], job_data["salary"], job_data["highly_preferred_skills"], job_data["active"], job_id
            ),)
            con.commit()
            logSQL(f"Job {job_id} updated successfully", "update_job")
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "update_job", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.put("/update/resume/{uid}")
async def update_resume(uid: str, resume_data: dict):
    """
    Update a resume.

    Args:
        uid (str): User ID.
        resume_data (dict): Resume data to be updated.
        Example:
        {
            "uid": "1234567890",
            "resume_data": {
                "skills": ["updated_skill1", "updated_skill2"],
                "experience": ["updated_experience1", "updated_experience2"],
                "education": ["updated_education1", "updated_education2"]
            }
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Resume updated successfully",
            "status_code": 100
        }
    
    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logAPI(f"Updating resume for user {uid}", "update_resume", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("UPDATE resumes SET skills = %s, experience = %s, education = %s WHERE uid = %s", (json.dumps(resume_data["skills"]), json.dumps(resume_data["experience"]), json.dumps(resume_data["education"]), uid))
            con.commit()
            logSQL(f"Resume for user {uid} updated successfully", "update_resume")
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "update_resume", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.put("/update/profile/{uid}")
async def update_profile(uid: str, profile: Profile):
    """
    Update the profile of a user.

    Args:
        uid (str): User ID.
        profile (Profile): Profile object containing the updated user data.
        Example:
        {
            "uid": "1234567890",
            "name": "John Doe",
            "dob": "01011999",
            "is_owner": false,
            "is_admin": false,
            "resume_data": {
                "skills": ["updated_skill1", "updated_skill2"],
                "experience": ["updated_experience1", "updated_experience2"],
                "education": ["updated_education1", "updated_education2"]
            },
            "phone_number": "+XX-XXXXXXXXXX",
            "email": "john.doe@example.com"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Profile updated successfully",
            "status_code": 100
        }
    
    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logAPI(f"Updating profile for user {uid}", "update_profile", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET name = %s, dob = %s, is_owner = %s, is_admin = %s, phone_number = %s, email = %s
                WHERE uid = %s
            """, (profile.name, profile.dob, profile.is_owner, profile.is_admin, profile.phone_number, profile.email, uid))
            
            cursor.execute("UPDATE resumes SET skills = %s, experience = %s, education = %s WHERE uid = %s",
                           (json.dumps(profile.resume_data.skills), json.dumps(profile.resume_data.experience), json.dumps(profile.resume_data.education), uid))
            
            con.commit()
            logSQL(f"Profile for user {uid} updated successfully", "update_profile")
    except psycopg2.Error as e:
        logAPI(f"An error occurred: {e}", "update_profile", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)
#endregion

#region Logging Endpoints
def logSQL(msg: str, func: str, level: str = "INFO"):
    print(f"[ResumeGraderAPI] [SQL] [{level}] ({func}): {msg};")

def logAPI(msg: str, func: str, level: str = "INFO"):
    print(f"[ResumeGraderAPI] [{level}] [API]({func}): {msg};")
#endregion

#region print Tables
@app.get("/printTables/USERS")
def print_users():
    con = connection_pool.getconn()
    users = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            for user in results:
                users.append(user)
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return users

@app.get("/printTables/RESUMES")
def print_resumes():
    con = connection_pool.getconn()
    resumes = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM resumes")
            results = cursor.fetchall()
            for resume in results:
                resumes.append(resume)
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return resumes

@app.get("/printTables/JOBDESCRIPTIONS")
def print_jobs():
    con = connection_pool.getconn()
    jobs = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM jobdescriptions")
            results = cursor.fetchall()
            for job in results:
                jobs.append(job)
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return jobs


@app.get("/printTables/MATCHES")
def print_matches():
    con = connection_pool.getconn()
    matches = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM matches")
            results = cursor.fetchall()
            for match in results:
                matches.append(match)
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return matches

@app.get("/printTables/FEEDBACK")
def print_feedback():
    con = connection_pool.getconn()
    feedbacks = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM feedback")
            results = cursor.fetchall()
            for feedback in results:
                feedbacks.append(feedback)
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return feedbacks

@app.get("/printTables/Profiles")
def print_profiles():
    con = connection_pool.getconn()
    profiles = []
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            for user in results:
                cursor.execute("SELECT * FROM resumes WHERE uid = %s", (user[0],))
                resume = cursor.fetchone()
                profiles.append({"uid": user[0], "name": user[1], "dob": user[2], "is_owner": user[3], "is_admin": user[4], "phone_number": user[5], "email": user[6], "resume": resume})
    except psycopg2.Error as e:
        print(e)
    finally:
        if con:
            connection_pool.putconn(con)
    return profiles
#endregion

#region DELETE endpoints
@app.delete("/delete/user/{uid}")
def delete_user(uid: str):
    """
    Delete a user by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "User deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting user {uid}", "delete_user", "INFO")
    con = connection_pool.getconn()
    try:
        delete_resume(uid)
        delete_matches(uid)
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE uid = %s", (uid,))
            con.commit()
            logSQL(f"User {uid} deleted successfully", "delete_user")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_user", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/resume/{uid}")
def delete_resume(uid: str):
    """
    Delete a resume by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Resume deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting resume for user {uid}", "delete_resume", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM resumes WHERE uid = %s", (uid,))
            con.commit()
            logSQL(f"Resume for user {uid} deleted successfully", "delete_resume")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_resume", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/job/{job_id}")
def delete_job(job_id: int):
    """
    Delete a job by job ID.

    Args:
        job_id (int): Job ID.
        Example:
        {
            "job_id": 1
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Job deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting job {job_id}", "delete_job", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM jobdescriptions WHERE job_id = %s", (job_id,))
            con.commit()
            logSQL(f"Job {job_id} deleted successfully", "delete_job")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_job", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/matches/{uid}")
def delete_matches(uid: str):
    """
    Delete matches by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "1234567890"
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Matches deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting matches for user {uid}", "delete_matches", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT match_id FROM matches WHERE uid = %s", (uid,))
            matches = cursor.fetchall()
            for match in matches:
                delete_feedbacks(match[0])
            cursor.execute("DELETE FROM matches WHERE uid = %s", (uid,))
            con.commit()
            logSQL(f"Matches for user {uid} deleted successfully", "delete_matches")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_matches", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/match/{match_id}")
def delete_match(match_id: int):
    """
    Delete a match by match ID.

    Args:
        match_id (int): Match ID.
        Example:
        {
            "match_id": 1
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Match deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting match {match_id}", "delete_match", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT match_id FROM matches WHERE uid = %s", (uid,))
            matches = cursor.fetchall()
            for match in matches:
                delete_feedbacks(match[0])
            cursor.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
            con.commit()
            logSQL(f"Match {match_id} deleted successfully", "delete_match")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_match", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/feedback/{feedback_id}")
def delete_feedback(feedback_id: int):
    """
    Delete feedback by feedback ID.

    Args:
        feedback_id (int): Feedback ID.
        Example:
        {
            "feedback_id": 1
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Feedback deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting feedback {feedback_id}", "delete_feedback", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM feedback WHERE feedback_id = %s", (feedback_id,))
            con.commit()
            logSQL(f"Feedback {feedback_id} deleted successfully", "delete_feedback")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_feedback", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.delete("/delete/feedback/matchId/{match_id}")
def delete_feedbacks(match_id: int):
    """
    Delete feedbacks by match ID.

    Args:
        match_id (int): Match ID.
        Example:
        {
            "match_id": 1
        }

    Returns:
        dict: Dictionary containing the status of the operation.
        Example:
        {
            "status": "Feedbacks deleted successfully",
            "status_code": 100
        }

    Raises:
        HTTPException: If an error occurs during the deletion process.
    """
    logAPI(f"Deleting feedbacks for match {match_id}", "delete_feedbacks", "INFO")
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM feedback WHERE match_id = %s", (match_id,))
            con.commit()
            logSQL(f"Feedbacks for match {match_id} deleted successfully", "delete_feedbacks")
    except psycopg2.Error as e:
        logSQL(f"An error occurred: {e}", "delete_feedbacks", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)
#endregion

import os
import asyncio

async def create_temp_file(content: str, suffix: str) -> UploadFile:
    temp_file_path = Path(f"temp{suffix}")
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    with temp_file_path.open("wb") as buffer:
        buffer.write(content.encode())
    return UploadFile(filename=temp_file_path.name, file=open(temp_file_path, 'rb'))

async def main():
    uid = ""

    # Test with TXT file
    txt_file = await create_temp_file("Sample resume content lkasjdfla klkfdsja lfsjkfal j fsajf dweb sdeveloper ", ".txt")
    try:
        response = await extract_resume(api_key, uid, txt_file)
        print("TXT File Response:", response)
    finally:
        txt_file.file.close()
        os.remove("" + txt_file.filename)

if __name__ == "__main__":
    asyncio.run(main())
