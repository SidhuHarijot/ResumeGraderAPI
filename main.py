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

class ApplicationData(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume.")
    job_id: int = Field(..., description="Unique identifier for the job.")

class Resume(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume.")
    resume_data: dict = Field(..., description="Data pertaining to the resume.")

class Job(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    job_data: dict = Field(..., description="Data pertaining to the job.")
    active: bool = Field(..., description="Status of the job, whether it is active or not.")

class Grade(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume being graded.")
    job_id: int = Field(..., description="Unique identifier for the job related to the grade.")
    grade: int = Field(..., description="Grade assigned to the resume for the specified job.")

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the job application.")
    resume_id: int = Field(..., description="Unique identifier of the resume used in the application.")
    job_id: int = Field(..., description="Unique identifier of the job applied for.")
    application_date: datetime = Field(..., description="Date when the application was submitted.")
    status: str = Field(..., description="Current status of the application.")
    status_code: int = Field(..., description="Numerical code representing the status of the application.")

class ResumeWithGrade(BaseModel):
    resume_id: int = Field(..., description="Unique identifier for the resume.")
    resume_data: Dict = Field(..., description="Data of the resume.")
    grade: Optional[int] = Field(None, description="Optional grade assigned to the resume.")

class GradingRequest(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    resume_id: int = Field(default=-1, description="Unique identifier for the resume, default is -1 indicating no specific resume.")
    apiKey: str = Field(..., description="API key for authentication.")
    maxGrade: int = Field(default=1, description="Maximum grade that can be assigned.")
#endregion

#region Grading Endpoints
@app.post("/grade/ChatGPT/", response_model=Grade)
async def grade_resume(request: GradingRequest):
    if request.resume_id == -1:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    grade = await _grade_resume_chatGPT(request.apiKey, request.job_id, [request.resume_id], request.maxGrade)
    grade = grade[request.resume_id]
    result = await save_grade(request.resume_id, request.job_id, grade)
    return result

async def save_grade(resume_id: int, job_id: int, grade: int):
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO grades (resume_id, job_id, grade)
                VALUES (%s, %s, %s)
                ON CONFLICT (resume_id, job_id) DO UPDATE SET grade = EXCLUDED.grade
            """, (resume_id, job_id, grade))
            con.commit()
        return Grade(resume_id=resume_id, job_id=job_id, grade=grade)
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to save grade: {str(e)}")

async def _grade_resume_chatGPT(api_key, jobId: int, resumeIds: List[int], maxGrade):
    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")
    grades = {}

    jobDescription = str(getJob(jobId))
    resumeList = [getResume(resumeId) for resumeId in resumeIds]

    systemString = f"Grade resumes for this job description: \"{jobDescription}\" Maximum grade is {maxGrade}. " + \
                   "Just answer in the number or the grade nothing else. " + \
                   "Return -2 if resume is irrelevant to the job description" + \
                   "Return -1 if job description is not understandable or if the resume data has nothing or not understandable or enough to make good judgement." + \
                   "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Also be harsh with your evaluations"

    messages = [{"role": "system", "content": systemString}]

    for resume in resumeList:
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
async def gradeAllFromJob(request: GradingRequest):
    statusCode = 502
    status = "Error Unknown"
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT resume_id FROM matches WHERE job_id = %s", (request.job_id,))
            resume_ids = cursor.fetchall()
            cursor.execute("SELECT job_data FROM jobs WHERE job_id = %s", (request.job_id,))
            job_data = cursor.fetchone()
            if job_data:
                grades = await _grade_resume_chatGPT(request.apiKey, request.job_id, resume_ids, request.maxGrade)
                for resume_id, grade in grades.items():
                    cursor.execute("INSERT INTO grades (resume_id, job_id, grade) VALUES (%s, %s, %s)", (resume_id, request.job_id, grade))
                con.commit()
                statusCode = 100
                status = ""
            else:
                statusCode = 404
                status = "Job not found"
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        statusCode = 500
    finally:
        connection_pool.putconn(con)
    return {"status": applicationCodes[statusCode] + status, "statusCode": statusCode, "grades": grades}
#endregion

#region Extracting Endpoints
@app.post("/extract/resumeJSON/ChatGPT")
def extractResumeJSON(requestData: ExtractRequestData):
    client = OpenAI(api_key=requestData.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    systemString = """
    Convert the given resume data into a structured JSON format. Adhere strictly to this format: 
    {
        "name": ["FirstName", "LastName"], 
        "phoneNo": "+XX-XXXXXXXXXX", 
        "email": "email@example.com", 
        "experience": [{"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}, {"DDMMYYYY-DDMMYYYY": {"COMPANY NAME": "DESCRIPTION"}}],
        "skills": ["skill1", "skill2"],
        "education": [{"DDMMYYYY-DDMMYYYY": {"INSTITUTION": "COURSE NAME"}}],
        "certificates": {"institution name": "certificate name"}
    }
    Dates must be formatted as DDMMYYYY or 00000000 if no date is available.
    Ensure the phone number format includes a hyphen between the country code and the number. 
    It is critical that you follow the format precisely as described to ensure the data can be parsed correctly by the program without errors.
    """ 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemString},
            {"role": "user", "content": requestData.stringData}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

@app.post("/extract/jobDescriptionJSON/ChatGPT")
def extractJobDescriptionJSON(requestData: ExtractRequestData):
    client = OpenAI(api_key=requestData.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    systemString = """
    Convert the given job description data into a structured JSON format. Adhere strictly to this format: 
    {
        "Title": "Job Title",
        "description": "Job Description",
        "employer": "Employer Name",
        "Must Haves": ["Requirement 1", "Requirement 2"],
    }
    Ensure that the job description is concise and clearly describes the role, responsibilities, and requirements for the position.
    for must have requirements, List them only if given in the job description. Must haves are the responsibilities or requirements that are mandatory for the job.
    """ 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemString},
            {"role": "user", "content": requestData.stringData}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
#endregion

#region checkPermission Endpoints
def checkIdAdmin(uid: str):
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM Users WHERE uid = %s", (uid,))
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return False

def checkIsOwner(uid: str):
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            cursor.execute("SELECT is_owner FROM Users WHERE uid = %s", (uid,))
            return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return False
#endregion

#region Upload Endpoints
@app.post("/upload/resume/")
async def upload_resume(apiKey: str, file: UploadFile = File(...)):
    try:
        temp_file_path = await save_temp_file(file)
        resume_text = await extract_text(temp_file_path)
        data = ExtractRequestData(stringData=resume_text, apiKey=apiKey)
        resume_json = extractResumeJSON(data)
        temp_file_path.unlink() 
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract resume data: {str(e)}")
    return await save_resume_data(resume_json)

@app.post("/upload/job/")
async def upload_job(apiKey: str, file: UploadFile = File(...)):
    try:
        temp_file_path = await save_temp_file(file)
        job_text = await extract_text(temp_file_path)
        job_json = extractJobDescriptionJSON(ExtractRequestData(stringData=job_text, apiKey=apiKey))
        temp_file_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract job data: {str(e)}")
    return await save_job_data(job_json)

async def save_temp_file(file: UploadFile):
    temp_file_path = Path(f"temp_files/{file.filename}")
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_file_path

async def extract_text(file_path: Path):
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

async def save_resume_data(resume_data: dict):
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO resumes (resume_data) VALUES (%s) RETURNING resume_id", (json.dumps(resume_data),))
            resume_id = cursor.fetchone()[0]
            con.commit()
        return {"status": "Resume uploaded successfully", "resume_id": resume_id}
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload resume, error: {str(e)}")
    finally:
        connection_pool.putconn(con)

async def save_job_data(job_data: dict):
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO jobdescriptions (job_data) VALUES (%s) RETURNING job_id", (json.dumps(job_data),))
            job_id = cursor.fetchone()[0]
            con.commit()
        return {"status": "Job uploaded successfully", "job_id": job_id}
    except psycopg2.Error as e:
        return {"status": "Failed to upload job", "error": str(e)}

@app.post("/upload/application")
def uploadApplication(data: ApplicationData):
    statusCode = 502
    status = "Error Unknown"
    applicationId = -1
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO matches (resume_id, job_id) VALUES (%s, %s) RETURNING match_id", (data.resume_id, data.job_id))
            applicationId = cursor.fetchone()[0]
            con.commit()
        statusCode = 100
        status = ""
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        statusCode = 500
    finally:
        connection_pool.putconn(con)
    return {"status": applicationCodes[statusCode]  + status, "statusCode": statusCode, "application_id": applicationId}
#endregion

#region SQL Endpoints
@app.post("/createTables")
def createTables():
    sqlError = ""
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            tables = {
                "Users": """
                    CREATE TABLE Users (
                        user_id SERIAL PRIMARY KEY,
                        uid VARCHAR(50) NOT NULL,
                        is_owner BOOLEAN DEFAULT FALSE,
                        username VARCHAR(50) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        password_hash VARCHAR(100) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE, 
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """,
                "Resumes": """
                    CREATE TABLE Resumes (
                        resume_id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        resume_file VARCHAR(2000) NOT NULL,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id)
                    );
                """,
                "JobDescriptions": """
                    CREATE TABLE JobDescriptions (
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
                        rating DECIMAL(5, 2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """,
                "Matches": """
                    CREATE TABLE Matches (
                        match_id SERIAL PRIMARY KEY,
                        resume_id INT NOT NULL,
                        job_id INT NOT NULL,
                        match_percentage DECIMAL(5, 2),
                        highly_preferred_skills VARCHAR(100)[],
                        low_preferred_skills VARCHAR(100)[],
                        rating DECIMAL(5, 2),
                        FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id),
                        FOREIGN KEY (job_id) REFERENCES JobDescriptions(job_id)
                    );
                """,
                "Feedback": """
                    CREATE TABLE Feedback (
                        feedback_id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        resume_id INT NOT NULL,
                        feedback_text TEXT NOT NULL,
                        rating INT CHECK (rating >= 1 AND rating <= 5),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES Users(user_id),
                        FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id)
                    );
                """
            }
            for table_name, table_schema in tables.items().__reversed__():
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            for table_name, table_schema in tables.items():
                cursor.execute(f"CREATE TABLE {table_name} ({table_schema})")
            con.commit() 
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        sqlError = str(e)
    finally:
        connection_pool.putconn(con)

    if sqlError != "":
        return {"status": "Tables created successfully", "statusCode": 200} 
    else:
        return {"status": "An error occurred while creating tables, " + sqlError, "sqlError": sqlError, "statusCode": 500}
#endregion

#region Retrieve Endpoints
@app.get("/retrieve/resume/{resume_id}", response_model=Resume)
def getResume(resume_id: int):
    resume = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM resumes WHERE resume_id = %s", (resume_id,))
            resume = cursor.fetchone()
            resume_data = json.loads(resume[1])
            resume = Resume(resume_id=resume[0], resume_data=resume_data)
            print("[RETREIVED RESUME]: ", resume)
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return resume


@app.get("/retrieve/job/{job_id}", response_model=Job)
def getJob(job_id: int):
    job = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM jobdescriptions WHERE job_id = %s", (job_id,))
            job = cursor.fetchone()
            job_data = json.loads(job[1])
            job = Job(job_id=job[0], job_data=job_data, active=job[2])
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return job


@app.get("/retrieve/match/{match_id}", response_model=Match)
def getMatch(match_id: int):
    match = None
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("SELECT * FROM matches WHERE match_id = %s", (match_id,))
            match = cursor.fetchone()
            match = Match(match_id=match[0], resume_id=match[1], job_id=match[2], application_date=match[3], status=match[4], status_code=match[5])
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection_pool.putconn(con)
    return match


@app.get("/retrieve/resumes/", response_model=List[Resume])
async def get_resumes(resume_id: Optional[int] = None):
    con = connection_pool.getconn()
    try:
        with con.cursor() as cursor:
            if resume_id:
                cursor.execute("SELECT * FROM resumes WHERE resume_id = %s", (resume_id,))
            else:
                cursor.execute("SELECT * FROM resumes")
            results = cursor.fetchall()
            return [Resume(resume_id=resume[0], resume_data=json.loads(resume[1])) for resume in results]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)


@app.get("/retrieve/jobs/", response_model=List[Job])
async def get_jobs(active: Optional[bool] = None):
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


@app.get("/retrieve/grades/", response_model=List[Grade])
async def get_grades(resume_id: Optional[int] = None, job_id: Optional[int] = None):
    con = connection_pool.getconn()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM grades"
            conditions = []
            params = []
            if resume_id:
                conditions.append("resume_id = %s")
                params.append(resume_id)
            if job_id:
                conditions.append("job_id = %s")
                params.append(job_id)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            return [Grade(**grade) for grade in results]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.get("/retrieve/resumes_with_grades/", response_model=List[ResumeWithGrade])
async def get_resumes_with_grades(job_id: int):
    con = connection_pool.getconn()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
            SELECT r.resume_id, r.resume_data, g.grade
            FROM resumes r
            LEFT JOIN grades g ON r.resume_id = g.resume_id AND g.job_id = %s
            WHERE EXISTS (
                SELECT 1 FROM grades WHERE job_id = %s AND resume_id = r.resume_id
            )
            """
            cursor.execute(query, (job_id, job_id))
            results = cursor.fetchall()
            return [ResumeWithGrade(**resume) for resume in results]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)
#endregion

#region Update Endpoints
@app.put("/update/user/makeAdmin/{user_id}")
async def make_user_admin(user_id: int, owner_uid: str):
    con = connection_pool.getconn()
    try:
        if not checkIsOwner(owner_uid):
            raise HTTPException(status_code=403, detail="You do not have permission to make this user an admin.")
        with con.cursor() as cursor:
            cursor.execute("UPDATE Users SET is_admin = TRUE WHERE user_id = %s", (user_id))
            con.commit()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if con:
            connection_pool.putconn(con)

@app.put("/update/job/{job_id}")
async def update_job(job_id: int, job_data: dict):
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
#endregion
