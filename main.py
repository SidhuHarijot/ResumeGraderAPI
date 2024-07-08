# region imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List, Optional
from Models.DataModels.GetModels import *
from Database.database import *
from Processing.DataValidation.Validation import Validation
from Processing.authorize import Authorize
from ServerLogging.serverLogger import Logger
from pathlib import Path
import shutil
from Models.RequestModels.GetModels import RequestModels as rm
from Services.services import *
import datetime
from Processing.Factories.GetFactories import *
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
import traceback
import os
import sys
from Utilities.OpenAIUtility import OpenAIUtility
from Services.getServices import *
import asyncio

# endregion


# region Initialize
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


# Initialize logger
Logger.initialize()
# Initialize database connection
Database.initialize()
# Initialize OpenAI utility
OpenAIUtility.initialize()

def log(message, func):
    Logger.logMain(message, func, "INFO")

def logError(message, e: Exception, func):
    message = f"{message}\n{traceback.format_exception(None, e, e.__traceback__)}"
    Logger.logMain(message, func, "ERROR")

# add logs to middleware
@app.middleware("http")
async def add_logs(request, call_next):
    log(f"Request to {request.url.path}", "main.add_logs")
    response = await call_next(request)
    log(f"Response from {request.url.path}", "main.add_logs")
    return response


# Add directory to python path
def add_current_directory_to_path():
    current_directory = os.getcwd()
    if current_directory not in sys.path:
        sys.path.append(current_directory)
        log(f"Added {current_directory} to PYTHONPATH", "main.add_current_directory_to_path")
    else:
        log(f"{current_directory} is already in PYTHONPATH", "main.add_current_directory_to_path")
# endregion

# region doc customization
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/darkDocs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_css_url="/static/swagger_ui_dark.min.css"
    )
# endregion

# region Root
@app.get("/", tags=["Root"])
async def read_root() -> HTMLResponse:
    """Root endpoint for the API. Returns a welcome message and information about the API.
    
    :rtype: HTMLResponse
    
    Params:
        None

    Returns:
        HTMLResponse: An HTML response containing the welcome message and API information.
        
    Raises:
        HTTPException: If an error occurs while accessing the root endpoint.
    """
    try:
        log("Accessing root endpoint", "read_root")
        html_data = """
        <html>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 50px;
                }
                h1 {
                    color: #333;
                }
                p {
                    color: #666;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
            <head>
                <title>Job Matching System API</title>
            </head>
            <body>
                <h1>Welcome to the API!</h1>
                <p>This is a FastAPI project backend for a job matching system.</p>
                <p>Author: BugSlayerz.HarijotSingh</p>
                <p>Technologies used: FastAPI, PostgreSQL, Firebase, Python</p>
                <p>Contact us:
                    <a href="mailto:sidhuharijot@gmail.com"><strong>Email</strong></a>
                </p>
                <p>Version: 4.0</p>
                <p>Documentation:
                    <a href="/docs"><strong>Swagger UI</strong></a>
                    <a href="/redoc"><strong>ReDoc</strong></a>
                    <a href="/darkDocs"><strong>Dark Swagger UI</strong></a>
                </p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_data, status_code=200)
    except Exception as e:
        logError(f"Error in root endpoint: ", e, "read_root")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Users
@app.post("/users/", response_model=User, tags=["Users"])
async def create_user(request: rm.User.Create) -> User:
    """Creates a new user with the provided data.
    
    :param request: The request object containing the user data.
    :type request: rm.User.Create
    
    :rtype: User
    
    Example:
        request:
        {
            "uid": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "01012000",
            "phone_number": "00-1234567890",
            "email": "abc@email.com"
        }

    Returns:
        User: The user object created.
        Example:
        {
            "uid": "12345",
            "name": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "dob": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "is_owner": false,
            "is_admin": false,
            "phone_number": "00-1234567890",
            "email": "abc@email.com"
        }

    Raises:
        HTTPException: If an error occurs while creating the user.
    """
    try:
        userService = UserService(new_user=request)
        userService.save_to_db()
        return userService.user
    except HTTPException as e:
        logError(f"Validation error in create_user: ", e, "create_user")
        raise e
    except Exception as e:
        logError(f"Error in create_user: ", e, "create_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/users/{uid}", response_model=User, tags=["Users"])
async def get_user(uid: str) -> User:
    """Retrieves a user with the provided UID.

    :param uid: The UID of the user to retrieve.
    :type uid: str
    
    :rtype: User

    Example:
        "12345"

    Returns:
        User: The user object retrieved.
        Example:
        {
            "uid": "12345",
            "name": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "dob": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "is_owner": false,
            "is_admin": false,
            "phone_number": "00-1234567890",
            "email": "abc@email.com"
        }

    Raises:
        HTTPException: If an error occurs while retrieving the user.
    """
    try:
        userService = UserService.get_from_db(uid)
        return userService.user
    except Exception as e:
        logError(f"Error in get_user: ", e, "get_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/users/", response_model=User, tags=["Users"])
async def update_user(request: rm.User.Update) -> User:
    """Updates a user with the provided data.
    
    :param uid: The UID of the user to update.
    :type uid: str
    :param request: The request object containing the updated user data.
    :type request: rm.User.Update
    
    :rtype: User
    
    Example:
        request:
        {
            "uid": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "01012000",
            "phone_number": "00-1234567890",
            "email": "abc@email.com",
            "is_owner": false,
            "is_admin": false
        }

    Returns:
        User: The user object updated.
        Example:
        {
            "uid": "12345",
            "name": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "dob": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "is_owner": false,
            "is_admin": false,
            "phone_number": "00-1234567890",
            "email": "abc@email.com"
        }

    Raises:
        HTTPException: If an error occurs while updating the user.
    """
    try:
        log(f"Updating user with UID: {request.uid}", "update_user")
        userService = UserService.get_from_db(request.uid)
        userService.update(request)
        return userService.user
    except HTTPException as e:
        logError(f"Validation error in update_user: ", e, "update_user")
        raise e
    except Exception as e:
        logError(f"Error in update_user: ", e, "update_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/users/{uid}", tags=["Users"])
async def delete_user(uid: str) -> dict:
    """Deletes a user with the provided UID.

    :param uid: The UID of the user to delete.
    :type uid: str
    
    :rtype: dict

    Example:
        "12345"

    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "User deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs while deleting the user.
    """
    try:
        log(f"Deleting user with UID: {uid}", "delete_user")
        us = UserService.get_from_db(uid)
        us.delete()
        return {"message": "User deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_user: ", e, "delete_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_all_users(auth_uid: str) -> List[User]:
    """Retrieves all users.

    :param auth_uid: The UID of the user requesting the information.
    :type auth_uid: str
    
    :rtype: List[User]

    Example:
        "12345"

    Returns:
        List[User]: A list of all users.
        Example:
        [
            {
                "uid": "12345",
                "name": {
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "dob": {
                    "day": 1,
                    "month": 1,
                    "year": 2000
                },
                "is_owner": false,
                "is_admin": false,
                "phone_number": "00-1234567890",
                "email": "abc@email.com"
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all users.
    """
    try:
        log("Retrieving all users", "get_all_users")
        if not (Authorize.checkAuth(auth_uid, "ADMIN") or Authorize.checkAuth(auth_uid, "OWNER")):
            raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
        
        return UserService.get_all()
    except HTTPException as e:
        logError(f"Authorization error in get_all_users: ", e, "get_all_users")
        raise e
    except Exception as e:
        logError(f"Error in get_all_users: ", e, "get_all_users")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region User Privileges
@app.get("/users/privileges/{uid}", response_model=str, tags=["Users"])
async def get_user_privileges(uid: str) -> str:
    """Retrieves the privileges of a user with the provided UID.

    :param uid: The UID of the user whose privileges are to be retrieved.
    :type uid: str
    
    :rtype: str

    Example:
        "12345"

    Returns:
        str: The privilege level of the user.
        Example:
        "ADMIN"

    Raises:
        HTTPException: If an error occurs while retrieving the user's privileges.
    """
    try:
        log(f"Retrieving user privileges for UID: {uid}", "get_user_privileges")
        if Authorize.checkAuth(uid, "OWNER"):
            return "OWNER"
        elif Authorize.checkAuth(uid, "ADMIN"):
            return "ADMIN"
        else:
            return "USER"
    except Exception as e:
        logError(f"Error in get_user_privileges: ", e, "get_user_privileges")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/users/privileges", tags=["Users"])
async def update_user_privileges(request: rm.User.Privileges.Update) -> dict:
    """Updates the privileges of a user with the provided data.
    
    :param request: The request object containing the updated user privileges.
    :type request: rm.User.Privileges.Update
    
    :rtype: dict
    
    Example:
        request:
        {
            "target_uid": "12345",
            "is_admin": false,
            "is_owner": false
        }

    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "User privileges updated successfully."
        }

    Raises:
        HTTPException: If an error occurs while updating the user privileges.
    """
    try:
        log("Updating user privileges", "update_user_privileges")
        AuthService.update_privileges(request)
        return {"message": "User privileges updated successfully."}
    except PermissionError as e:
        logError(f"Authorization error in update_user_privileges: ", e, "update_user_privileges")
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except HTTPException as e:
        logError(f"Authorization or validation error in update_user_privileges: ", e, "update_user_privileges")
        raise e
    except Exception as e:
        logError(f"Error in update_user_privileges: ", e, "update_user_privileges")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Resumes
@app.post("/resumes/", response_model=Resume, tags=["Resumes"])
async def create_resume(request: rm.Resumes.Create) -> Resume:
    """Creates a new resume with the provided data.
    
    :param uid: The UID of the user associated with the resume.
    :type uid: str
    :param request: The request object containing the resume data.
    :type request: rm.Resumes.Create
    
    :rtype: Resume
    
    Example:
        request:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": "01012000",
                    "end_date": "01012001",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "01012000",
                    "end_date": "01012001",
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ],
            "file": "resume.pdf",
            "resume_text": "John Doe Software Engineer Skills: Python, Java, SQL Experience: 2 years Education: Bachelor's in Computer Science"
        }

    Returns:
        Resume: The resume object created.
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ]
        }

    Raises:
        HTTPException: If an error occurs while creating the resume.
    """
    try:
        log("Creating a new resume", "create_resume")
        resumeS = ResumeService.create_from_request(request, None)
        return resumeS.resume
    except HTTPException as e:
        logError(f"Validation error in create_resume: ", e, "create_resume")
        raise e
    except Exception as e:
        logError(f"Error in create_resume: ", e, "create_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/resumes/{uid}", tags=["Resumes"])
async def upload_resume(uid: str, file: UploadFile=File(...)) -> Resume:
    """Uploads a resume file for a user with the provided UID.
    
    :param uid: The UID of the user associated with the resume.
    :type uid: str
    :param file: The resume file to upload.
    :type file: UploadFile
        
    
    :rtype: Resume
    
    Example:
        "12345"
        resume.pdf
        
    Returns:
        
        Resume: The resume object created.
        
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ]
        }

    Raises:
        HTTPException: If an error occurs while uploading the resume.
    """
    try:
        log(f"Uploading resume for UID: {uid}", "upload_resume")
        resumeS = ResumeService.create_from_request(rm.Resumes.Create(uid=uid), file)
        return resumeS.resume
    except HTTPException as e:
        logError(f"Validation error in upload_resume: ", e, "upload_resume")
        raise e
    except Exception as e:
        logError(f"Error in upload_resume: ", e, "upload_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def get_resume(uid: str) -> Resume:
    """Retrieves a resume with the provided UID.
    
    :param uid: The UID of the resume to retrieve.
    :type uid: str
    
    :rtype: Resume

    Example:
        "12345"
            
    Returns:
        Resume: The resume object retrieved.
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ]
        }

    Raises:
        HTTPException: If an error occurs while retrieving the resume.
    """
    try:
        log(f"Retrieving resume with UID: {uid}", "get_resume")
        return ResumeDatabase.get_resume(uid)
    except ValueError as e:
        logError(f"Resume not found: {uid}", e, "get_resume")
        raise HTTPException(status_code=404, detail="Resume not found.")
    except Exception as e:
        logError(f"Error in get_resume: ", e, "get_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/resumes/", response_model=Resume, tags=["Resumes"])
async def update_resume(request: rm.Resumes.Update) -> Resume:
    """Updates a resume with the provided data.
    
    :param uid: The UID of the resume to update.
    :type uid: str
    :param request: The request object containing the updated resume data.
    :type request: rm.Resumes.Update
    
    :rtype: Resume
    
    Example:
        uid:
        "12345"
        request:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": "01012000",
                    "end_date": "01012001",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "01012000",
                    "end_date": "01012001",
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ]
        }

    Returns:
        Resume: The resume object updated.
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2000
                    },
                    "end_date": {
                        "day": 1,
                        "month": 1,
                        "year": 2001
                    },
                    "institution": "Institution",
                    "course_name": "Course Name"
                }
            ]
        }

    Raises:
        HTTPException: If an error occurs while updating the resume.
    """
    try:
        log(f"Updating resume with UID: {request.uid}", "update_resume")
        resumeS = ResumeService.create_from_db(request.uid)
        resumeS.update(request)
        return resumeS.resume
    except HTTPException as e:
        logError(f"Validation error in update_resume: ", e, "update_resume")
        raise e
    except Exception as e:
        logError(f"Error in update_resume: ", e, "update_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/resumes/{uid}", tags=["Resumes"])
async def delete_resume(uid: str):
    """Deletes a resume with the provided UID.

    :param uid: The UID of the resume to delete.
    :type uid: str
    
    :rtype: dict

    Example:
        "12345"

    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "Resume deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs while deleting the resume.
    """
    try:
        log(f"Deleting resume with UID: {uid}", "delete_resume")
        ResumeService.delete_from_db(uid)
        return {"message": "Resume deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_resume: ", e, "delete_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Jobs
@app.post("/jobs/", response_model=Job, tags=["Jobs"])
async def create_job(request: rm.Jobs.Create=Depends()) -> Job:
    """Creates a new job with the provided data.
    
    :param request: The request object containing the job data.
    :type request: rm.Jobs.Create
    
    :rtype: Job
    
    Example:
        request:
        {
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": "01012000",
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true,
            "file": "job_description.pdf",
            "auth_uid": "12345"
        }

    Returns:
        Job: The job object created.
        Example:
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true
        }

    Raises:
        HTTPException: If an error occurs while creating the job.
    """
    try:
        log("Creating a new job", "create_job")
        jobS = JobService.create_from_request(request, None)
        return jobS.job
    except PermissionError as e:
        logError(f"Authorization error in create_job: ", e, "create_job")
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except HTTPException as e:
        logError(f"Validation error in create_job: ", e, "create_job")
        raise e
    except Exception as e:
        logError(f"Error in create_job: ", e, "create_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/jobs/{auth_uid}", tags=["Jobs"])
async def upload_job_file(auth_uid: str, file: UploadFile=File(...)) -> Job:
    """Uploads a file for a job with the provided ID.
    
    :param job_id: The ID of the job to upload the file for.
    :type job_id: int
    :param file: The file to upload.
    :type file: UploadFile
    
    :rtype: dict
    
    Example:
        1
        job_description.pdf
        
    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "File uploaded successfully."
        }

    Raises:
        HTTPException: If an error occurs while uploading the file.
    """
    try:
        log(f"Uploading file for job.", "upload_job_file")
        jS = JobService.create_from_request(rm.Jobs.Create(auth_uid=auth_uid), file)
        return jS.job
    except PermissionError as e:
        logError(f"Authorization error in upload_job_file: ", e, "upload_job_file")
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except HTTPException as e:
        logError(f"Validation error in upload_job_file: ", e, "upload_job_file")
        raise e
    except Exception as e:
        logError(f"Error in upload_job_file: ", e, "upload_job_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def get_job(job_id: int) -> Job:
    """Retrieves a job with the provided ID.
    
    :param job_id: The ID of the job to retrieve.
    :type job_id: int
    
    :rtype: Job

    Example:
        1
            
    Returns:
        Job: The job object retrieved.
        Example:
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true
        }

    Raises:
        HTTPException: If an error occurs while retrieving the job.
    """
    try:
        log(f"Retrieving job with ID: {job_id}", "get_job")
        return JobService.get_from_db(job_id).job
    except Exception as e:
        logError(f"Error in get_job: ", e, "get_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/jobs/", response_model=Job, tags=["Jobs"])
async def update_job(request: rm.Jobs.Update) -> Job:
    """Updates a job with the provided data.
    
    :param job_id: The ID of the job to update.
    :type job_id: int
    :param request: The request object containing the updated job data.
    :type request: rm.Jobs.Update
    
    :rtype: Job
    
    Example:
        request:
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": "01012000",
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true,
            "auth_uid": "12345"
        }

    Returns:
        Job: The job object updated.
        Example:
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": {
                "day": 1,
                "month": 1,
                "year": 2000
            },
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true
        }

    Raises:
        HTTPException: If an error occurs while updating the job.
    """
    try:
        log(f"Updating job with ID: {request.job_id}", "update_job")
        jobS = JobService.get_from_db(request.job_id)
        jobS.update(request)
        return jobS.job
    except PermissionError as e:
        logError(f"Authorization error in update_job: ", e, "update_job")
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except ValueError as e:
        logError(f"Job not found: {request.job_id}", e, "update_job")
        raise HTTPException(status_code=404, detail="Job not found.")
    except HTTPException as e:
        logError(f"Validation error in update_job: ", e, "update_job")
        raise e
    except Exception as e:
        logError(f"Error in update_job: ", e, "update_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: int) -> dict:
    """Deletes a job with the provided ID.
    
    :param job_id: The ID of the job to delete.
    :type job_id: int
    
    :rtype: dict

    Example:
        1
            
    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "Job deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs while deleting the job.
    """
    try:
        log(f"Deleting job with ID: {job_id}", "delete_job")
        JobDatabase.delete_job(job_id)
        return {"message": "Job deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_job: ", e, "delete_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/jobs/", response_model=List[Job], tags=["Jobs"])
async def get_all_jobs(active: Optional[bool]=Query(None, description="Get all active jobs"),
                    skills: Optional[List[str]]=Query(None, description="Get jobs for specific skills")) -> List[Job]:
    """Retrieves all jobs.
    
    :rtype: List[Job]

    Params:
        active: Get all active jobs.
        skills: Get jobs for specific skills.

        example:
        active: true
        skills: ["Python", "Java", "SQL"]

    Returns:
        List[Job]: A list of all jobs.
        Example:
        [
            {
                "job_id": 1,
                "title": "Software Engineer",
                "company": "XYZ",
                "description": "Job Description",
                "required_skills": ["Python", "Java", "SQL"],
                "application_deadline": {
                    "day": 1,
                    "month": 1,
                    "year": 2000
                },
                "location": "Location",
                "salary": 100000,
                "job_type": "FULL",
                "active": true
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all jobs.
    """
    try:
        log("Retrieving all jobs", "get_all_jobs")
        request = rm.Jobs.Get(active=active, skills=skills)
        return JobService.get_multiple_jobs_from_db(request)
    except ValueError:
        logError(f"No jobs found", "get_all_jobs")
        raise HTTPException(status_code=404, detail="No jobs found.")
    except Exception as e:
        logError(f"Error in get_all_jobs: ", e, "get_all_jobs")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Matches
@app.post("/matches/", response_model=Match, tags=["Matches"])
async def create_match(request: rm.Matches.Create) -> Match:
    """Creates a new match with the provided data.
    
    :param request: The request object containing the match data.
    :type request: rm.Matches.Create
    
    :rtype: Match
    
    Example:
        request:
        {
            "uid": "12345",
            "job_id": 1,
            "selected_skills": ["skill1", "skill2"]
        }

    Returns:
        Match: The match object created.
        Example:
        {
            "match_id": 1,
            "uid": "12345",
            "job_id": 1,
            "status": "PENDING",
            "status_code": 0,
            "grade": -1,
            "selected_skills": [],
        }

    Raises:
        HTTPException: If an error occurs while creating the match.
    """
    try:
        log("Creating a new match", "create_match")
        matchS:MatchService = MatchService.create_from_request(request)
        return matchS.match
    except HTTPException as e:
        logError(f"Validation error in create_match: ", e, "create_match")
        raise e
    except Exception as e:
        logError(f"Error in create_match: ", e, "create_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def get_match(match_id: int) -> Match:
    """Retrieves a match with the provided ID.
    
    :param match_id: The ID of the match to retrieve.
    :type match_id: int
    
    :rtype: Match

    Example:
        1
            
    Returns:
        Match: The match object retrieved.
        Example:
        {
            "match_id": 1,
            "uid": "12345",
            "job_id": 1,
            "status": "PENDING"
        }

    Raises:
        HTTPException: If an error occurs while retrieving the match.
    """
    try:
        log(f"Retrieving match with match id: {match_id}", "get_match")
        return MatchService.get_from_db(match_id).match
    except Exception as e:
        logError(f"Error in get_match: ", e, "get_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def update_match(request: rm.Matches.Update) -> Match:
    """Updates a match with the provided data.
    
    :param match_id: The ID of the match to update.
    :type match_id: int
    :param request: The request object containing the updated match data.
    :type request: rm.Matches.Update
    
    :rtype: Match
    
    Example:
        match_id:
        1
        request:
        {
            "uid": "12345",
            "job_id": 1,
            "status": "ACCEPTED"
        }

    Returns:
        Match: The match object updated.
        Example:
        {
            "match_id": 1,
            "uid": "12345",
            "job_id": 1,
            "status": "ACCEPTED"
        }

    Raises:
        HTTPException: If an error occurs while updating the match.
    """
    try:
        log(f"Updating match with ID: {request.match_id}", "update_match")
        matchS = MatchService.get_from_db(request.match_id)
        matchS.update_from_request(request)
        return matchS.match
    except HTTPException as e:
        logError(f"Validation error in update_match: ", e, "update_match")
        raise e
    except Exception as e:
        logError(f"Error in update_match: ", e, "update_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/matches/{match_id}", tags=["Matches"])
async def delete_match(match_id: int) -> dict:
    """Deletes a match with the provided ID.
    
    :param match_id: The ID of the match to delete.
    :type match_id: int
    
    :rtype: dict

    Example:
        1
            
    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "Match deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs while deleting the match.
    """
    try:
        log(f"Deleting match with ID: {match_id}", "delete_match")
        MatchService.delete_from_db(match_id)
        return {"message": "Match deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_match: ", e, "delete_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/", response_model=List[Match], tags=["Matches"])
async def get_all_matches(request: rm.Matches.Get = Depends()) -> List[Match]:
    """Retrieves all matches.
    
    :rtype: List[Match]

    Returns:
        List[Match]: A list of all matches.
        Example:
        [
            {
                "match_id": 1,
                "uid": "12345",
                "job_id": 1,
                "status": "PENDING"
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all matches.
    """
    try:
        log("Retrieving all matches", "get_all_matches")
        return MatchService.get_from_request(request)
    except Exception as e:
        logError(f"Error in get_all_matches: ", e, "get_all_matches")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Feedback
@app.post("/feedback/", response_model=Feedback, tags=["Feedback"])
async def create_feedback(request: rm.Feedback.Create) -> Feedback:
    """Creates a new feedback with the provided data.
    
    :param request: The request object containing the feedback data.
    :type request: rm.Feedback.Create
    
    :rtype: Feedback
    
    Example:
        request:
        {
            "match_id": 1,
            "feedback_text": "Great job!"
        }

    Returns:
        Feedback: The feedback object created.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great job!"
        }

    Raises:
        HTTPException: If an error occurs while creating the feedback.
    """
    try:
        log("Creating a new feedback", "create_feedback")
        return FeedbackService.create_feedback(request).feedback
    except HTTPException as e:
        logError(f"Validation error in create_feedback: ", e, "create_feedback")
        raise e
    except Exception as e:
        logError(f"Error in create_feedback: ", e, "create_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def get_feedback(feedback_id: int) -> Feedback:
    """Retrieves a feedback with the provided ID.
    
    :param feedback_id: The ID of the feedback to retrieve.
    :type feedback_id: int
    
    :rtype: Feedback

    Example:
        1
            
    Returns:
        Feedback: The feedback object retrieved.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great job!"
        }

    Raises:
        HTTPException: If an error occurs while retrieving the feedback.
    """
    try:
        log(f"Retrieving feedback with ID: {feedback_id}", "get_feedback")
        return FeedbackService.get_feedback(feedback_id).feedback
    except Exception as e:
        logError(f"Error in get_feedback: ", e, "get_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def update_feedback(request: rm.Feedback.Update) -> Feedback:
    """Updates a feedback with the provided data.
    
    :param feedback_id: The ID of the feedback to update.
    :type feedback_id: int
    :param request: The request object containing the updated feedback data.
    :type request: rm.Feedback.Update
    
    :rtype: Feedback
    
    Example:
        feedback_id:
        1
        request:
        {
            "feedback_text": "Excellent job!"
        }

    Returns:
        Feedback: The feedback object updated.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Excellent job!"
        }

    Raises:
        HTTPException: If an error occurs while updating the feedback.
    """
    try:
        log(f"Updating feedback with ID: {request.feedback_id}", "update_feedback")
        return FeedbackService.update_feedback(request).feedback
    except HTTPException as e:
        logError(f"Validation error in update_feedback: ", e, "update_feedback")
        raise e
    except Exception as e:
        logError(f"Error in update_feedback: ", e, "update_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/feedback/{feedback_id}", tags=["Feedback"])
async def delete_feedback(feedback_id: int) -> dict:
    """Deletes a feedback with the provided ID.
    
    :param feedback_id: The ID of the feedback to delete.
    :type feedback_id: int
    
    :rtype: dict

    Example:
        1
            
    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "Feedback deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs while deleting the feedback.
    """
    try:
        log(f"Deleting feedback with ID: {feedback_id}", "delete_feedback")
        FeedbackService.delete_feedback(feedback_id)
        return {"message": "Feedback deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_feedback: ", e, "delete_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/", response_model=List[Feedback], tags=["Feedback"])
async def get_multiple_feedbacks(request: rm.Feedback.Get=Depends()) -> List[Feedback]:
    """Retrieves all feedbacks.
    
    :rtype: List[Feedback]

    Returns:
        List[Feedback]: A list of all feedbacks.
        Example:
        [
            {
                "feedback_id": 1,
                "match_id": 1,
                "feedback_text": "Great job!"
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all feedbacks.
    """
    try:
        return FeedbackService.get_feedbacks(request)
    except Exception as e:
        logError(f"Error in get_all_feedbacks: ", e, "get_all_feedbacks")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Logs
@app.get("/logs/download", tags=["Logs"])
async def download_logs() -> FileResponse:
    """Downloads the log files as a zip archive.
    
    :rtype: FileResponse
    
    Params:
        None
        
    Returns:
        FileResponse: The zip archive containing the log files.
        
    Raises:
        HTTPException: If an error occurs while downloading the logs.
    """
    log_folder = Path(Logger.logFolder)
    decompressed_folder = Path(Logger.decompressed)

    try:
        log("Downloading logs", "download_logs")
        # Ensure logs are decompressed
        Logger.compressLogs()
        Logger.decompressLogs()

        # Create a zip of the logs
        zip_path = log_folder / "logs.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), 'zip', decompressed_folder)
        Logger.clearDecompressedLogs()
        return FileResponse(str(zip_path), filename="logs.zip", media_type='application/zip')
    except Exception as e:
        logError(f"Error in download_logs: ", e, "download_logs")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Clean up decompressed log files
        for file in log_folder.glob("*.txt"):
            if file.name != datetime.datetime.now().strftime("logs%d-%m-%Y.txt"):
                file.unlink()

@app.post("/logs/compress", tags=["Logs"])
async def compress_logs() -> dict:
    """Compresses the log files into a zip archive.

    :rtype: dict

    Params:
        None
    
    Returns:
        dict: A dictionary containing a success message.
        Example:
        {
            "message": "Logs compressed successfully."
        }
    
    Raises:
        HTTPException: If an error occurs while compressing the logs.
    """
    try:
        log("Compressing logs", "compress_logs")
        Logger.compressLogs()
        return {"message": "Logs compressed successfully."}
    except Exception as e:
        logError(f"Error in compress_logs: ", e, "compress_logs")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region Grading
@app.post("/grade/job/{job_id}", tags=["Grading"])
async def grade_job(job_id: int) -> List[Match]:
    """Grades resumes for a job.
    
    :param job_id: The ID of the job for which to grade resumes.
    :type job_id: int
    
    :rtype: List[Match]
    
    Example:
        job_id:
        1
    
    Returns:
        List[Match]: A list of matches for the job.
        Example:
        [
            {
                "match_id": 1,
                "uid": "12345",
                "job_id": 1,
                "status": "PENDING"
            }
        ]
    
    Raises:
        HTTPException: If an error occurs while grading the job.
    """
    try:
        log("Grading job", "grade_job")
        matches = GradingService.grade_resumes_for_job(job_id=job_id)
        return matches
    except Exception as e:
        logError(f"Error in grade_job: ", e, "grade_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion

# region DebugPrints:
@app.get("/print/users/{auth_id}", tags=["Debug"], include_in_schema=False)
def printUsers(auth_id: str):
    try:
        log(f"Printing all users for UID: {auth_id}", "printUsers")
        request = rm.User.Privileges.Update(target_uid="", auth_uid=auth_id)
        return HTMLResponse(UserService.print_all(request))
    except PermissionError:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except Exception as e:
        logError(f"Error in printUsers: ", e, "printUsers")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/print/resumes/{auth_id}", tags=["Debug"], include_in_schema=False)
def printResumes(auth_id: str):
    try:
        log(f"Printing all resumes for UID: {auth_id}", "printResumes")
        request = rm.User.Privileges.Update(target_uid="", auth_uid=auth_id)
        return HTMLResponse(ResumeService.print_all(request))
    except PermissionError:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except Exception as e:
        logError(f"Error in printResumes: ", e, "printResumes")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/print/jobs/{auth_id}", tags=["Debug"], include_in_schema=False)
def printJobs(auth_id: str):
    try:
        log(f"Printing all jobs for UID: {auth_id}", "printJobs")
        request = rm.User.Privileges.Update(target_uid="", auth_uid=auth_id)
        return HTMLResponse(JobService.print_all(request))
    except PermissionError:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except Exception as e:
        logError(f"Error in printJobs: ", e, "printJobs")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/print/matches/{auth_id}", tags=["Debug"], include_in_schema=False)
def printMatches(auth_id: str):
    try:
        log(f"Printing all matches for UID: {auth_id}", "printMatches")
        request = rm.User.Privileges.Update(target_uid="", auth_uid=auth_id)
        return HTMLResponse(MatchService.print_all(request))
    except PermissionError:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except Exception as e:
        logError(f"Error in printMatches: ", e, "printMatches")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/print/feedback/{auth_id}", tags=["Debug"], include_in_schema=False)
def printFeedback(auth_id: str):
    try:
        log(f"Printing all feedback for UID: {auth_id}", "printFeedback")
        request = rm.User.Privileges.Update(target_uid="", auth_uid=auth_id)
        return HTMLResponse(FeedbackService.print_all(request))
    except PermissionError:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    except Exception as e:
        logError(f"Error in printFeedback: ", e, "printFeedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# endregion
