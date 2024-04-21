from fastapi import FastAPI, File, UploadFile
from mangum import Mangum
from pydantic import BaseModel, model_validator
from openai import OpenAI
import PyPDF2 as pypdf2
import docx2txt
import psycopg2
import psycopg2.pool
from fastapi.middleware.cors import CORSMiddleware
import json


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
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # Minimum number of idle connections in the pool
        10, # Maximum number of connections allowed
        database="resume_grader",
        user="bugslayerz",
        password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
        host="dpg-coi9t65jm4es739kjul0-a.oregon-postgres.render.com"
    )
    if connection_pool:
        print("Connection pool created successfully")
except (Exception, psycopg2.DatabaseError) as error:
    print("Error while connecting to PostgreSQL", error)
#endregion

#region Fast API Initialization
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost:3000", 
    "https://your-nextjs-deployment-url.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
#endregion


#region Pydantic Models
class GradeRequestData(BaseModel):
    resumeData: dict[int, str]
    jobDescription:str
    noOfResumes: int
    apiKey: str

    @model_validator(mode="after")
    def checkResumeCount(self):
        if len(self.resumeData) != self.noOfResumes:
            raise ValueError("No of resumes does not match the number of resume data provided in the resumeData")
        return self


class ExtractRequestData(BaseModel):
    stringData: str
    apiKey: str


class ApplicationData(BaseModel):
    resume_id: int
    job_id: int
#endregion

handler = Mangum(app)

@app.get("/")
def read_root():
    return {"version": "1.0",
            "author": "Harijot Singh",
            "Title": "Resume Grader",
            "Description": "This is an API to grade resumes for a provided job description."}

#region Grading Endpoints
@app.post("/grade/ChatGPT/{maxGrade}")
async def grade_chatgpt(maxGrade: int, requestData: GradeRequestData):
    """
    grades resumes using ChatGPT model.
    Args:
    - maxGrade (int): The maximum possible grade.
    - requestData (GradeRequestData): The request data containing the resume data and job description.

    Returns:
    - dict: A dictionary containing the grades for each resume and an error log.
    """
    grades: dict[int, int] = {}
    errorLog = {}
    ids = [*requestData.resumeData.keys()]
    resumeData = [*requestData.resumeData.values()]
    response = await _grade_resume_chatGPT(requestData.apiKey, requestData.jobDescription, resumeData, maxGrade)
    for i in range(len(ids)):
        if "Error: " not in response[i]:
            grades[ids[i]] = int(response[i])
        else:
            errorLog[ids[i]] = response[i]
    return {"Grades" : grades, "errorLog": errorLog}


async def _grade_resume_chatGPT(api_key, jobDescription, resumeList, maxGrade):
    """
    Grades a resume based on a job description using GPT-4.
    
    Args:
    - api_key (str): The API key for authenticating with the OpenAI API.
    - jobDescription (str): System description, e.g., "Grade resumes for a Software Engineer position. Maximum grade: 100."
    - resumeList (List[str]): List of resumes
    - maxGrade (int): The maximum possible grade.

    Returns:
    - List[str]: A list of grades for each resume.
    """

    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")
    grades = []

    systemString = f"Grade resumes for this job description: \"{jobDescription}\" Maximum grade is {maxGrade}. " + \
                   "Just answer in the number or the grade nothing else. " + \
                   "Return -2 if resume is irrelevant to the job description" + \
                   "Return -1 if job description is not understandable or if the resume data has nothing or not understandable or enough to make good judgement." + \
                   "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Also be harsh with your evaluations"

    messages = [{"role": "system", "content": systemString}]

    for resume in resumeList:
        individual_messages = messages.copy()  # Copy the base messages list
        individual_messages.append({"role": "user", "content": resume})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=individual_messages
            )
            # Assuming each response contains a number directly (you may need to parse or process text)
            last_message = response.choices[0].message.content.strip()
            if int(last_message) == -1:
                grades.append("Error: ChatGPT could not grade the resume, based on the given data.")
            else:
                grades.append(last_message)
        except Exception as e:
            grades.append("Error: " + str(e))

    return grades

@app.post("/grade/ChatGPT/")
async def grade_chatgpt(requestData: GradeRequestData):
    """
    grades resumes using ChatGPT model.
    Args:
    - requestData (GradeRequestData): The request data containing the resume data and job description.

    Returns:
    - dict: A dictionary containing the grades for each resume and an error log.
    """
    grades: dict[int, int] = {}
    errorLog = {}
    ids = [*requestData.resumeData.keys()]
    resumeData = [*requestData.resumeData.values()]
    response = await _grade_resume_chatGPT(requestData.apiKey, requestData.jobDescription, resumeData, 1)
    for i in range(len(ids)):
        if "Error: " not in response[i]:
            grades[ids[i]] = int(response[i])
        else:
            errorLog[ids[i]] = response[i]
    return {"Grades" : grades, "errorLog": errorLog}
#endregion

#region Extracting Endpoints
@app.post("/extract/Text/{filetype}")
def extractFromFile(filetype: str, file: UploadFile = File(...)):
    """
    Extracts resume data from a file.
    Args:
    - filetype (str): The type of the file, e.g., "pdf", "docx", etc.
    - file (UploadFile): The file to extract data from.

    Returns:
    - dict: A dictionary containing the extracted resume data.
    """
    extractedText = ""
    if filetype == "docx":
        extractedText = docx2txt.process(file.file)
    elif filetype == "pdf":
        extractedText = pypdf2.PdfReader(file.file).pages[0].extract_text()
    elif filetype == "txt":
        extractedText = file.file.read().decode("utf-8")
    return {"extractedText" : extractedText}


@app.post("/extract/resumeJSON/ChatGPT")
def extractResumeJSON(requestData: ExtractRequestData):
    """
    Extracts resume data from a str and converts it to JSON format with ChatGPT.
    Args:
    - dataString (str): The resume data in string format.
    - api_key (str): The API key for authenticating with the OpenAI API.

    Returns:
    - dict: A dictionary containing the extracted resume data in JSON format.
    """
    client = OpenAI(api_key=requestData.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    systemString = "Use the given resume data to and convert it to json format. " + \
    "The format would be: {name: [firstName, lastName], phoneNo: '+XX-XXXXXXXXXX', email: email, " + \
    "experience: [\{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}, \{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}],"+\
    "skills: ['skill1', 'skill2'], education: [\{'DDMMYYYY-DDMMYYYY': \{'INSTITUTION': 'COURSE NAME'\}\}, ...]," + \
    "certificates: \{'institution name': 'certificate name'\}\}  for dates if none given use 00000000" + \
    "the keys in the list should exactly be the same as in the format no matter what is being used in the resume data." + \
    "You have to adhere strictly to the format given, you cant use July 2024 for dates convert it to like 00072024 " + \
    "Similarly for phone number just use hyper between the country code and the number. like +XX-XXXXXXXXXX so that the data is consistent. " 
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


#region Upload Endpoints
@app.post("/upload/job")
def uploadJob(jobData: dict[str, str]):
    """
    Uploads a job description file.
    Args:
    - file (UploadFile): The job description file to upload.

    Returns:
    - dict: A dictionary containing the status of the upload.
    """
    status = ""
    statusCode = 200
    job_id = -1
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO jobs (job_data) VALUES (%s)", (jobData))
            job_id = cursor.fetchone()[0]
            con.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        status = str(e)
        statusCode = 500
    finally:
        connection_pool.putconn(con)
    return {"status": status, "statusCode": statusCode, "id": job_id}

@app.post("/upload/resume")
def uploadResume(resumeData: dict[str, str]):
    """
    Uploads resume data
    Args:
    - resumeData (dict[str, str]): The resume data to upload.

    Returns:
    - dict: A dictionary containing the status of the upload.
    """
    status = ""
    statusCode = 200
    try:
        con = connection_pool.getconn()
        resume_id = -1
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO resume (resume_Data) VALUES (%s)", (resumeData))
            resume_id = cursor.fetchone()[0]
            con.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        status = str(e)
        statusCode = 500
    finally:
        connection_pool.putconn(con)
    return {"status": status, "statusCode": statusCode, "id": resume_id}

@app.post("/upload/application")
def uploadApplication(data: ApplicationData):
    """
    Uploads an application.
    Args:
    - data (ApplicationData): The application data to upload.

    Returns:
    - dict: A dictionary containing the status of the upload.
    """
    statusCode = 502
    status = "Error Unknown"
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO applications (resume_id, job_id) VALUES (%s, %s)", (data.resume_id, data.job_id))
            con.commit()
        statusCode = 100
        status = ""
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        con.rollback()
        statusCode = 500
    finally:
        connection_pool.putconn(con)
    return {"status": applicationCodes[statusCode]  + status, "statusCode": statusCode}
    
#endregion

#region SQL Endpoints
@app.post("/createTables")
def createTables():
    sqlError = ""
    try:
        con = connection_pool.getconn()
        with con.cursor() as cursor:
            tables = {
                "resume": """
                    resume_id SERIAL PRIMARY KEY,
                    resume_data JSON
                """,
                "jobs": """
                    job_id SERIAL PRIMARY KEY,
                    job_data JSON,
                    active BOOLEAN DEFAULT TRUE
                """,
                "grades": """
                    resume_id INT,
                    job_id INT,
                    grade INT,
                    PRIMARY KEY (resume_id, job_id),
                    FOREIGN KEY (resume_id) REFERENCES resume(resume_id),
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                """,
                "applications": """
                    application_id SERIAL PRIMARY KEY,
                    resume_id INT,
                    job_id INT,
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    statusCode INT,
                    FOREIGN KEY (resume_id) REFERENCES resume(resume_id),
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                """
            }
            for table_name, table_schema in tables.items():
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
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

if __name__ == "__main__":
    createTables()
    uploadJob({"Title": "Software Engineer", "description": "Grade resumes for a Software Engineer position.", "employer": "Google"})
