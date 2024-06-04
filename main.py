# region Imports
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
from datetime import datetime
from psycopg2.extras import RealDictCursor
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

class ExtractRequestData(BaseModel):
    stringData: str = Field(..., description="String data to be extracted.")
    apiKey: str = Field(..., description="API key for authentication.")

class Resume(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume.")
    user_id: int = Field(..., description="User ID associated with the resume.")
    skills: List[str] = Field(..., description="List of skills")
    experience: List[str] = Field(..., description="List of experiences")
    education: List[str] = Field(..., description="List of educations")

class Job(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    job_data: dict = Field(..., description="Data pertaining to the job.")
    active: bool = Field(..., description="Status of the job, whether it is active or not.")

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the job application.")
    resume_id: int = Field(..., description="Unique identifier of the resume used in the application.")
    job_id: int = Field(..., description="Unique identifier of the job applied for.")
    match_percentage: Optional[float] = Field(None, description="Match percentage between resume and job.")
    highly_preferred_skills: Optional[List[str]] = Field(None, description="List of highly preferred skills.")
    low_preferred_skills: Optional[List[str]] = Field(None, description="List of low preferred skills.")
    rating: Optional[float] = Field(None, description="Rating of the match.")

class ResumeWithGrade(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume.")
    resume_data: Dict = Field(..., description="Data of the resume.")
    grade: Optional[int] = Field(None, description="Optional grade assigned to the resume.")

class GradingRequest(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    resume_id: int = Field(default=-1, description="Unique identifier for the resume, default is -1 indicating no specific resume.")
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
        request (GradingRequest): Request object containing job_id, resume_id, apiKey, and maxGrade.
        Example:
        {
            "job_id": 1,
            "resume_id": 1,
            "apiKey": "sk-XXXXXXXX",
            "maxGrade": 1
        }

    Returns:
        Match: Match object containing the resume_id, job_id, and grade.
        Example:
        {
            "match_id": 1,
            "resume_id": 1,
            "job_id": 1,
            "grade": 1
        }
    
    Raises:
        HTTPException: If an error occurs during grading.
    """
    if request.resume_id == -1:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    grade = await _grade_resume_chatGPT(request.apiKey, request.job_id, [request.resume_id], request.maxGrade)
    grade = grade[request.resume_id]
    result = await save_match(request.resume_id, request.job_id, grade)
    return result

async def save_match(resume_id: int, job_id: int, grade: int):
    """
    Save the match data to the database.

    Args:
        resume_id (int): Unique identifier for the resume.
        job_id (int): Unique identifier for the job.
        grade (int): Grade assigned to the resume.

    Returns:
        Match: Match object containing the resume_id, job_id, and grade.
        Example:
        {
            "match_id": 1,
            "resume_id": 1,
            "job_id": 1,
            "grade": 1
        }
    
    Raises:
        HTTPException: If an error occurs during saving.
    """
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO matches (resume_id, job_id, grade)
                VALUES (%s, %s, %s)
                ON CONFLICT (resume_id, job_id) DO UPDATE SET grade = EXCLUDED.grade
            """, (resume_id, job_id, grade))
            con.commit()
        return Match(resume_id=resume_id, job_id=job_id, grade=grade)
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to save match: {str(e)}")

async def _grade_resume_chatGPT(api_key, job_id: int, resume_ids: List[int], max_grade: int):
    """
    Grade resumes using ChatGPT.

    Args:
        api_key (str): OpenAI API key.
        job_id (int): Unique identifier for the job.
        resume_ids (List[int]): List of resume IDs to be graded.
        max_grade (int): Maximum grade that can be assigned.

    Returns:
        Dict[int, int]: Dictionary mapping resume IDs to their grades.
        Example:
        {
            1: 1,
            2: 0
        }
    
    Raises:
        Exception: If an error occurs during grading.
    """
    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")
    grades = {}

    job_description = str(get_job(job_id))
    resume_list = [get_resume(resume_id) for resume_id in resume_ids]

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
                grades[resume.resume_id] = -1
            else:
                grades[resume.resume_id] = int(last_message)
        except Exception as e:
            grades[resume.resume_id] = -1

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
                1: 1,
                2: 0
            }
        }
    
    Raises:
        HTTPException: If an error occurs during grading.
    """
    status_code = 502
    status = "Error Unknown"
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT resume_id FROM matches WHERE job_id = %s", (request.job_id,))
            resume_ids = cursor.fetchall()
            cursor.execute("SELECT job_data FROM jobdescriptions WHERE job_id = %s", (request.job_id,))
            job_data = cursor.fetchone()
            if job_data:
                grades = await _grade_resume_chatGPT(request.apiKey, request.job_id, resume_ids, request.maxGrade)
                for resume_id, grade in grades.items():
                    cursor.execute("""
                        INSERT INTO matches (resume_id, job_id, grade)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (resume_id, job_id) DO UPDATE SET grade = EXCLUDED.grade
                    """, (resume_id, request.job_id, grade))
                con.commit()
                status_code = 100
                status = ""
            else:
                status_code = 404
                status = "Job not found"
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        status_code = 500
    finally:
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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_string},
            {"role": "user", "content": request_data.stringData}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

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
    try:
        temp_file_path = await save_temp_file(file)
        resume_text = await extract_text(temp_file_path)
        data = ExtractRequestData(stringData=resume_text, apiKey=api_key)
        resume_json = extract_resume_json(data)
        temp_file_path.unlink()
        resume = Resume(
            resume_id=-1,
            user_id=-1,  # Placeholder, should be updated when saving to DB
            skills=resume_json["skills"],
            experience=resume_json["experience"],
            education=resume_json["education"]
        )
    except Exception as e:
        print(f"An error occurred: {e}")
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
    return response.choices[0].message.content
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
        print(f"An error occurred: {e}")
    finally:
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
        print(f"An error occurred: {e}")
    finally:
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
        dict: Dictionary containing the status and resume_id.
        Example:
        {
            "status": "Resume uploaded successfully",
            "resume_id": 1
        }
    
    Raises:
        HTTPException: If an error occurs during the upload.
    """
    try:
        temp_file_path = await save_temp_file(file)
        resume_text = await extract_text(temp_file_path)
        data = ExtractRequestData(stringData=resume_text, apiKey=api_key)
        resume_json = extract_resume_json(data)
        temp_file_path.unlink()
        resume = Resume(
            resume_id=-1,
            user_id=await get_user_id(uid),
            skills=resume_json["skills"],
            experience=resume_json["experience"],
            education=resume_json["education"]
        )
        return await save_resume_data(resume)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract resume data: {str(e)}")

@app.post("/upload/job/")
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
    try:
        temp_file_path = await save_temp_file(file)
        job_text = await extract_text(temp_file_path)
        job_json = extract_job_description_json(ExtractRequestData(stringData=job_text, apiKey=api_key))
        temp_file_path.unlink()
        return await save_job_data(job_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract job data: {str(e)}")

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

async def save_resume_data(resume_data: Resume):
    """
    Save the extracted resume data to the database.

    Args:
        resume_data (Resume): Extracted resume data.
        Example:
        {
            "resume_id": -1,
            "user_id": 1,
            "skills": ["skill1", "skill2"],
            "experience": ["experience1", "experience2"],
            "education": ["education1", "education2"]
        }

    Returns:
        dict: Dictionary containing the status and resume_id.
        Example:
        {
            "status": "Resume uploaded successfully",
            "resume_id": 1
        }
    
    Raises:
        HTTPException: If an error occurs during saving.
    """
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO resumes (user_id, skills, experience, education) VALUES (%s, %s, %s, %s) RETURNING resume_id", 
                           (resume_data.user_id, json.dumps(resume_data.skills), json.dumps(resume_data.experience), json.dumps(resume_data.education)))
            resume_id = cursor.fetchone()[0]
            con.commit()
        return {"status": "Resume uploaded successfully", "resume_id": resume_id}
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload resume, error: {str(e)}")
    finally:
        connection_pool.putconn(con)

async def save_job_data(job_data: dict):
    """
    Save the extracted job description data to the database.

    Args:
        job_data (dict): Extracted job description data.
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
            "low_preferred_skills": ["skill3", "skill4"],
            "rating": 4.5
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
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO jobdescriptions (title, company, description, required_skills, application_deadline, location, salary, highly_preferred_skills, low_preferred_skills, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING job_id", 
                           (job_data['title'], job_data['company'], job_data['description'], job_data['required_skills'], job_data['application_deadline'], job_data['location'], job_data['salary'], json.dumps(job_data['highly_preferred_skills']), json.dumps(job_data['low_preferred_skills']), job_data['rating']))
            job_id = cursor.fetchone()[0]
            con.commit()
        return {"status": "Job uploaded successfully", "job_id": job_id}
    except psycopg2.Error as e:
        return {"status": "Failed to upload job", "error": str(e)}
    finally:
        connection_pool.putconn(con)

@app.post("/upload/application")
def upload_application(data: Match):
    """
    Upload an application (match) to the database.

    Args:
        data (Match): Match data to be uploaded.
        Example:
        {
            "resume_id": 1,
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 1
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
    status_code = 502
    status = "Error Unknown"
    match_id = -1
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO matches (resume_id, job_id, status, status_code, grade) VALUES (%s, %s, %s, %s, %s) RETURNING match_id", 
                           (data.resume_id, data.job_id, data.status, data.status_code, data.grade))
            match_id = cursor.fetchone()[0]
            con.commit()
        status_code = 100
        status = ""
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        status_code = 500
    finally:
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
    status_code = 502
    status = "Error Unknown"
    try:
        data.is_owner = False
        data.is_admin = False
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (name, dob, uid, is_owner, is_admin, phone_number, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (uid) DO UPDATE SET name = EXCLUDED.name, dob = EXCLUDED.dob, is_owner = EXCLUDED.is_owner, is_admin = EXCLUDED.is_admin, phone_number = EXCLUDED.phone_number, email = EXCLUDED.email
            """, (data.name, data.dob, data.uid, data.is_owner, data.is_admin, data.phone_number, data.email))
            con.commit()
            status_code = 100
            status = ""
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        status_code = 500
    finally:
        connection_pool.putconn(con)
    return {"status": applicationCodes[status_code] + status, "status_code": status_code}
#endregion

#region SQL Endpoints
@app.post("/createTables")
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
    sql_error = ""
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            tables = {
                "users": """
                    CREATE TABLE users (
                        user_id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        dob DATE,
                        uid VARCHAR(50) NOT NULL,
                        is_owner BOOLEAN DEFAULT FALSE,
                        is_admin BOOLEAN DEFAULT FALSE,
                        phone_number VARCHAR(10),
                        email VARCHAR(100) NOT NULL UNIQUE
                    );
                """,
                "resumes": """
                    CREATE TABLE resumes (
                        resume_id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        skills VARCHAR(100)[],
                        experience VARCHAR(1000)[],
                        education VARCHAR(1000)[],
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    );
                """,
                "jobdescriptions": """
                    CREATE TABLE jobdescriptions (
                        job_id SERIAL PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        company VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        required_skills TEXT,
                        application_deadline DATE,
                        location VARCHAR(100),
                        salary DECIMAL(10, 2),
                        highly_preferred_skills VARCHAR(100)[],
                        low_preferred_skills VARCHAR(100)[],
                        rating DECIMAL(5, 2)
                    );
                """,
                "matches": """
                    CREATE TABLE matches (
                        match_id SERIAL PRIMARY KEY,
                        resume_id INT NOT NULL,
                        job_id INT NOT NULL,
                        match_percentage DECIMAL(5, 2),
                        status VARCHAR(100),
                        status_code INT,
                        grade INT,
                        highly_preferred_skills VARCHAR(100)[],
                        low_preferred_skills VARCHAR(100)[],
                        FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
                        FOREIGN KEY (job_id) REFERENCES jobdescriptions(job_id)
                    );
                """,
                "feedback": """
                    CREATE TABLE feedback (
                        feedback_id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        resume_id INT NOT NULL,
                        feedback_text TEXT NOT NULL,
                        rating INT CHECK (rating >= 1 AND rating <= 5),
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
                    );
                """
            }
            for table_name, table_schema in tables.items().__reversed__():
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            for table_name, table_schema in tables.items():
                cursor.execute(table_schema)
            con.commit() 
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        sql_error = str(e)
    finally:
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
            "resume_id": 1,
            "user_id": 1,
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
            cursor.execute("SELECT * FROM resumes WHERE user_id = (SELECT user_id FROM users WHERE uid = %s)", (uid,))
            resume = cursor.fetchone()
            if resume:
                resume_data = json.loads(resume[2])
                resume = Resume(resume_id=resume[0], user_id=resume[1], skills=resume_data['skills'], experience=resume_data['experience'], education=resume_data['education'])
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
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
                "highly_preferred_skills": ["skill1", "skill2"],
                "low_preferred_skills": ["skill3", "skill4"],
                "rating": 4.5
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
                job_data = json.loads(job[1])
                job = Job(job_id=job[0], job_data=job_data, active=job[2])
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
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
            "resume_id": 1,
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
                match = Match(match_id=match[0], resume_id=match[1], job_id=match[2], status=match[4], status_code=match[5], grade=match[6])
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return match

@app.get("/retrieve/resumes/", response_model=List[Resume])
async def get_resumes(resume_id: Optional[int] = None):
    """
    Retrieve all resumes or a specific resume by resume ID.

    Args:
        resume_id (Optional[int]): Resume ID (optional).
        Example:
        {
            "resume_id": 1
        }

    Returns:
        List[Resume]: List of Resume objects containing the resume data.
        Example:
        [
            {
                "resume_id": 1,
                "user_id": 1,
                "skills": ["skill1", "skill2"],
                "experience": ["experience1", "experience2"],
                "education": ["education1", "education2"]
            },
            {
                "resume_id": 2,
                "user_id": 2,
                "skills": ["skill3", "skill4"],
                "experience": ["experience3", "experience4"],
                "education": ["education3", "education4"]
            }
        ]
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            if resume_id:
                cursor.execute("SELECT * FROM resumes WHERE resume_id = %s", (resume_id,))
            else:
                cursor.execute("SELECT * FROM resumes")
            results = cursor.fetchall()
            return [Resume(resume_id=resume[0], user_id=resume[1], skills=json.loads(resume[2])['skills'], experience=json.loads(resume[2])['experience'], education=json.loads(resume[2])['education']) for resume in results]
    except psycopg2.Error as e:
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
                "job_data": {
                    "title": "Job Title",
                    "company": "Company Name",
                    "description": "Job Description",
                    "required_skills": "Skills",
                    "application_deadline": "2024-12-31",
                    "location": "Location",
                    "salary": 100000.00,
                    "highly_preferred_skills": ["skill1", "skill2"],
                    "low_preferred_skills": ["skill3", "skill4"],
                    "rating": 4.5
                },
                "active": true
            },
            {
                "job_id": 2,
                "job_data": {
                    "title": "Another Job Title",
                    "company": "Another Company",
                    "description": "Another Job Description",
                    "required_skills": "More Skills",
                    "application_deadline": "2024-12-31",
                    "location": "Another Location",
                    "salary": 120000.00,
                    "highly_preferred_skills": ["skill5", "skill6"],
                    "low_preferred_skills": ["skill7", "skill8"],
                    "rating": 4.7
                },
                "active": false
            }
        ]
    
    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            if active is not None:
                cursor.execute("SELECT * FROM jobdescriptions WHERE active = %s", (active,))
            else:
                cursor.execute("SELECT * FROM jobdescriptions")
            results = cursor.fetchall()
            
            return [Job(job_id=job[0], job_data=json.loads(job[1]), active=job[2]) for job in results]
    except psycopg2.Error as e:
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
                "resume_id": 1,
                "resume_data": {
                    "uid": "1234567890",
                    "skills": ["skill1", "skill2"],
                    "experience": ["experience1", "experience2"],
                    "education": ["education1", "education2"]
                },
                "grade": 1
            },
            {
                "resume_id": 2,
                "resume_data": {
                    "uid": "1234567891",
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            query = """
            SELECT r.resume_id, r.user_id, r.skills, r.experience, r.education, m.grade
            FROM resumes r
            LEFT JOIN matches m ON r.resume_id = m.resume_id AND m.job_id = %s
            WHERE EXISTS (
                SELECT 1 FROM matches WHERE job_id = %s AND resume_id = r.resume_id
            )
            """
            cursor.execute(query, (job_id, job_id))
            results = cursor.fetchall()
            return [ResumeWithGrade(resume_id=resume[0], resume_data={"user_id": resume[1], "skills": json.loads(resume[2])['skills'], "experience": json.loads(resume[2])['experience'], "education": json.loads(resume[2])['education']}, grade=resume[5]) for resume in results]
    except psycopg2.Error as e:
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if user:
                return User(
                    name=user[1],
                    dob=user[2],
                    uid=user[3],
                    is_owner=user[4],
                    is_admin=user[5],
                    phone_number=user[6],
                    email=user[7]
                )
    except psycopg2.Error as e:
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
                "resume_id": 1,
                "user_id": 1,
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if user:
                resume = get_resume(uid)
                return Profile(
                    uid=user[3],
                    name=user[1],
                    dob=user[2],
                    is_owner=user[4],
                    is_admin=user[5],
                    resume_data=resume,
                    phone_number=user[6],
                    email=user[7]
                )
    except psycopg2.Error as e:
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
    con = connection_pool.getconn()
    try:
        if not check_is_owner(owner_uid):
            raise HTTPException(status_code=403, detail="You do not have permission to make this user an admin.")
        with con.cursor() as cursor:
            cursor.execute("UPDATE users SET is_admin = TRUE WHERE uid = %s", (uid,))
            con.commit()
    except psycopg2.Error as e:
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
                "low_preferred_skills": ["updated_skill3", "updated_skill4"],
                "rating": 4.8
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("UPDATE jobdescriptions SET job_data = %s WHERE job_id = %s", (json.dumps(job_data), job_id))
            con.commit()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.put("/update/resume/{resume_id}")
async def update_resume(resume_id: int, resume_data: dict):
    """
    Update a resume.

    Args:
        resume_id (int): Resume ID.
        resume_data (dict): Resume data to be updated.
        Example:
        {
            "resume_id": 1,
            "resume_data": {
                "user_id": 1,
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("UPDATE resumes SET resume_data = %s WHERE resume_id = %s", (json.dumps(resume_data), resume_id))
            con.commit()
    except psycopg2.Error as e:
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
                "resume_id": 1,
                "user_id": 1,
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
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET name = %s, dob = %s, is_owner = %s, is_admin = %s, phone_number = %s, email = %s
                WHERE uid = %s
            """, (profile.name, profile.dob, profile.is_owner, profile.is_admin, profile.phone_number, profile.email, uid))
            
            cursor.execute("UPDATE resumes SET skills = %s, experience = %s, education = %s WHERE user_id = (SELECT user_id FROM users WHERE uid = %s)",
                           (json.dumps(profile.resume_data.skills), json.dumps(profile.resume_data.experience), json.dumps(profile.resume_data.education), uid))
            
            con.commit()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)
#endregion
