from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from datamodels import *
from database import *
from validation import Validation
from authorize import Authorize
from serverLogger import Logger
from pathlib import Path
import shutil
from requestmodels import *
from services import *
import datetime
from factories import *
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
import traceback

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


def log(message, func):
    Logger.logMain(message, func, "INFO")


def logError(message, e: Exception, func):
    message = f"{message}\n{traceback.format_exception(None, e, e.__traceback__)}"
    Logger.logMain(message, func, "ERROR")


@app.get("/", tags=["Root"])
async def read_root():
    try:
        log("Accessing root endpoint", "read_root")
        return {"message": "Welcome to the API!", "author": "BugSlayerz.HarijotSingh", "description": "This is a FastAPI project backend for a job matching system.", "Contact us": "sidhuharijot@gmail.com", "version": "3.0"}
    except Exception as e:
        logError(f"Error in root endpoint: ", e, "read_root")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/users/", response_model=User, tags=["Users"])
async def create_user(request: CreateUserRequest):
    """Creates a new user with the provided data.
    
    Params:
        request (CreateUserRequest): The request object containing the user data.
        Example:
        {
            "uid": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "dob": 
                {
                    "day": 1,
                    "month": 1,
                    "year": 2000
                },
            "is_owner": false,
            "is_admin": false,
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
            "dob": 
                {
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
        log("Creating a new user", "create_user")
        user = User(
            uid=request.uid,
            name=Name(first_name=request.first_name, last_name=request.last_name),
            dob=Date.from_string(request.dob),
            is_owner=False,
            is_admin=False,
            phone_number=request.phone_number,
            email=request.email
        )
        
        if not Validation.validate_user(user):
            raise HTTPException(status_code=400, detail="Invalid user data.")
        
        UserDatabase.create_user(user)
        return user
    except HTTPException as e:
        
        logError(f"Validation error in create_user: ", e, "create_user")
        raise e
    except Exception as e:
        
        logError(f"Error in create_user: ", e, "create_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/users/{uid}", response_model=User, tags=["Users"])
async def get_user(uid: str):
    """Retrieves a user with the provided UID.

    Params:
        uid (str): The UID of the user to retrieve.
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
            "dob": 
                {
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
        log(f"Retrieving user with UID: {uid}", "get_user")
        return UserDatabase.get_user(uid)
    except Exception as e:
        
        logError(f"Error in get_user: ", e, "get_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/users/{uid}", response_model=User, tags=["Users"])
async def update_user(uid: str, request: UpdateUserRequest):
    """Updates a user with the provided data.
    
    Params:
        uid (str): The UID of the user to update.
        Example:
            "12345"
        request (UpdateUserRequest): The request object containing the updated user data.
        Example:
        {
            "first_name": "John",
            "last_name": "Doe",
            "dob": "01022000",
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
            "dob": 
                {
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
        log(f"Updating user with UID: {uid}", "update_user")
        user = UserDatabase.get_user(uid)
        
        if request.first_name:
            user.name.first_name = request.first_name
        if request.last_name:
            user.name.last_name = request.last_name
        if request.dob:
            user.dob = Date.from_string(request.dob)
        if request.phone_number:
            user.phone_number = request.phone_number
        if request.email:
            user.email = request.email
        if request.is_owner is not None:
            user.is_owner = request.is_owner
        if request.is_admin is not None:
            user.is_admin = request.is_admin
        
        if not Validation.validate_user(user):
            raise HTTPException(status_code=400, detail="Invalid user data.")
        
        UserDatabase.update_user(user)
        return user
    except HTTPException as e:
        
        logError(f"Validation error in update_user: ", e, "update_user")
        raise e
    except Exception as e:
        
        logError(f"Error in update_user: ", e, "update_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/users/{uid}", tags=["Users"])
async def delete_user(uid: str):
    try:
        log(f"Deleting user with UID: {uid}", "delete_user")
        UserDatabase.delete_user(uid)
        return {"message": "User deleted successfully."}
    except Exception as e:
        
        logError(f"Error in delete_user: ", e, "delete_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_all_users(auth_uid: str):
    try:
        log("Retrieving all users", "get_all_users")
        if not (Authorize.checkAuth(auth_uid, "ADMIN") or Authorize.checkAuth(auth_uid, "OWNER")):
            raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
        
        return UserDatabase.get_all_users()
    except HTTPException as e:
        
        logError(f"Authorization error in get_all_users: ", e, "get_all_users")
        raise e
    except Exception as e:
        
        logError(f"Error in get_all_users: ", e, "get_all_users")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/users/privileges/{uid}", response_model=str, tags=["Users"])
async def get_user_privileges(uid: str):
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
async def update_user_privileges(request: UpdateUserPrivilegesRequest):
    try:
        log("Updating user privileges", "update_user_privileges")
        if not (Authorize.checkAuth(request.auth_uid, "ADMIN") or Authorize.checkAuth(request.auth_uid, "OWNER")):
            raise HTTPException(status_code=403, detail="You are not authorized to perform this action.")
        
        user = UserDatabase.get_user(request.target_uid)
        if request.is_admin is not None:
            user.is_admin = request.is_admin
        if request.is_owner is not None:
            user.is_owner = request.is_owner

        if not Validation.validate_user(user):
            raise HTTPException(status_code=400, detail="Invalid user data.")
        
        UserDatabase.update_user(user)
        return {"message": "User privileges updated successfully."}
    except HTTPException as e:
        
        logError(f"Authorization or validation error in update_user_privileges: ", e, "update_user_privileges")
        raise e
    except Exception as e:
        
        logError(f"Error in update_user_privileges: ", e, "update_user_privileges")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def create_resume(uid: str, file: UploadFile = File(None), resume_text: Optional[str] = None):
    """Creates a new resume with the provided data.
    
    Params:
        uid (str): The UID of the user associated with the resume.
        Example:
            "12345"
        file (UploadFile): The resume file to upload.
        resume_text (str): The text content of the resume.
        Example:
            "John Doe\nSoftware Engineer\nSkills: Python, Java, SQL\nExperience: 2 years\nEducation: Bachelor's in Computer Science"

    Returns:
        Resume: The resume object created.
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
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
        resume = ResumeService.process_resume(file, resume_text)
        
        if not Validation.validate_resume(resume):
            raise HTTPException(status_code=400, detail="Invalid resume data.")
        
        resume.uid = uid
        ResumeDatabase.create_resume(resume)
        return resume
    except HTTPException as e:
        
        logError(f"Validation error in create_resume: ", e, "create_resume")
        raise e
    except Exception as e:
        
        logError(f"Error in create_resume: ", e, "create_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def get_resume(uid: str):
    """Retrieves a resume with the provided UID.
    
    Params:
        uid (str): The UID of the resume to retrieve.
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
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
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
    except Exception as e:
        
        logError(f"Error in get_resume: ", e, "get_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def update_resume(uid: str, resume: Resume):
    """Updates a resume with the provided data.
    
    Params:
        uid (str): The UID of the resume to update.
        Example:
            "12345"
        resume (Resume): The resume object containing the updated data.
        Example:
        {
            "uid": "12345",
            "skills": ["Python", "Java", "SQL"],
            "experience": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
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
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                    "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
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
        log(f"Updating resume with UID: {uid}", "update_resume")
        if not Validation.validate_resume(resume):
            raise HTTPException(status_code=400, detail="Invalid resume data.")
        
        resume.uid = uid
        ResumeDatabase.update_resume(resume)
        return resume
    except HTTPException as e:
        
        logError(f"Validation error in update_resume: ", e, "update_resume")
        raise e
    except Exception as e:
        
        logError(f"Error in update_resume: ", e, "update_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/resumes/{uid}", tags=["Resumes"])
async def delete_resume(uid: str):
    try:
        log(f"Deleting resume with UID: {uid}", "delete_resume")
        ResumeDatabase.delete_resume(uid)
        return {"message": "Resume deleted successfully."}
    except Exception as e:
        
        logError(f"Error in delete_resume: ", e, "delete_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/resumes/", response_model=List[Resume], tags=["Resumes"])
async def get_all_resumes():
    """Retrieves all resumes.

    Params:
        None

    Returns:
        List[Resume]: A list of all resumes.
        Example:
        [
            {
                "uid": "12345",
                "skills": ["Python", "Java", "SQL"],
                "experience": [
                    {
                        "start_date": 
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                        "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                        "title": "Software Engineer",
                        "company_name": "Company",
                        "description": "Description of the experience."
                    }
                ],
                "education": [
                    {
                        "start_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                        "end_date":  
                            {
                                "day": 1,
                                "month": 1,
                                "year": 2000
                            },
                        "institution": "Institution",
                        "course_name": "Course Name"
                    }
                ]
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all resumes.
    """
    try:
        log("Retrieving all resumes", "get_all_resumes")
        return ResumeDatabase.get_all_resumes()
    except Exception as e:
        
        logError(f"Error in get_all_resumes: ", e, "get_all_resumes")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/jobs/", response_model=Job, tags=["Jobs"])
async def create_job(file: UploadFile = File(None), job_description_text: Optional[str] = None):
    """Creates a new job with the provided data.
    
    Params:
        file (UploadFile): The job description file to upload.
        job_description_text (str): The text content of the job description.
        Example:
            "Software Engineer\nCompany: XYZ\nDescription: Job Description\nMust Haves: Python, Java, SQL"
            
    Returns:
        Job: The job object created.
        Example:
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline":  
                {
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
        job = JobService.process_job_description(file, job_description_text)
        
        if not Validation.validate_job(job):
            raise HTTPException(status_code=400, detail="Invalid job data.")
        
        JobDatabase.create_job(job)
        return job
    except HTTPException as e:
        
        logError(f"Validation error in create_job: ", e, "create_job")
        raise e
    except Exception as e:
        
        logError(f"Error in create_job: ", e, "create_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def get_job(job_id: int):
    """Retrieves a job with the provided ID.
   / 
    Params:
        job_id (int): The ID of the job to retrieve.
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
            "application_deadline":  
                {
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
        return JobDatabase.get_job(job_id)
    except Exception as e:
        
        logError(f"Error in get_job: ", e, "get_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def update_job(job_id: int, request: UpdateJobRequest):
    """Updates a job with the provided data.
    
    Params:
        job_id (int): The ID of the job to update.
        Example:
            1
        request (UpdateJobRequest): The request object containing the updated job data.
        Example:
        {
            "title": "Software Engineer",
            "company": "XYZ",
            "description": "Job Description",
            "required_skills": ["Python", "Java", "SQL"],
            "application_deadline": "01-01-2000",
            "location": "Location",
            "salary": 100000,
            "job_type": "FULL",
            "active": true
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
            "application_deadline":  
                {
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
        log(f"Updating job with ID: {job_id}", "update_job")
        job = JobDatabase.get_job(job_id)
        
        if request.title:
            job.title = request.title
        if request.company:
            job.company = request.company
        if request.description:
            job.description = request.description
        if request.required_skills:
            job.required_skills = request.required_skills
        if request.application_deadline:
            job.application_deadline = Date.from_string(request.application_deadline)
        if request.location:
            job.location = request.location
        if request.salary is not None:
            job.salary = request.salary
        if request.job_type:
            job.job_type = request.job_type
        if request.active is not None:
            job.active = request.active
        
        if not Validation.validate_job(job):
            raise HTTPException(status_code=400, detail="Invalid job data.")
        
        JobDatabase.update_job(job)
        return job
    except HTTPException as e:
        
        logError(f"Validation error in update_job: ", e, "update_job")
        raise e
    except Exception as e:
        
        logError(f"Error in update_job: ", e, "update_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: int):
    """Deletes a job with the provided ID.
    
    Params:
        job_id (int): The ID of the job to delete.
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
async def get_all_jobs():
    """Retrieves all jobs.
    
    Params:
        None
        
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
                "application_deadline":  
                    {
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
        return JobDatabase.get_all_jobs()
    except Exception as e:
        
        logError(f"Error in get_all_jobs: ", e, "get_all_jobs")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/matches/", response_model=Match, tags=["Matches"])
async def create_match(match: Match):
    """Creates a new match with the provided data.
    
    Params:
        match (Match): The match object containing the match data.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "resume_id": 1,
            "status": "PENDING"
        }

    Returns:
        Match: The match object created.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "resume_id": 1,
            "status": "PENDING"
        }

    Raises:
        HTTPException: If an error occurs while creating the match.
    """
    try:
        log("Creating a new match", "create_match")
        if not Validation.validate_match(match):
            raise HTTPException(status_code=400, detail="Invalid match data.")
        
        MatchDatabase.create_match(match)
        return match
    except HTTPException as e:
        
        logError(f"Validation error in create_match: ", e, "create_match")
        raise e
    except Exception as e:
        
        logError(f"Error in create_match: ", e, "create_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def get_match(match_id: int):
    """Retrieves a match with the provided ID.
    
    Params:
        match_id (int): The ID of the match to retrieve.
        Example:
            1
            
    Returns:
        Match: The match object retrieved.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "resume_id": 1,
            "status": "PENDING"
        }

    Raises:
        HTTPException: If an error occurs while retrieving the match.
    """
    try:
        log(f"Retrieving match with ID: {match_id}", "get_match")
        return MatchDatabase.get_match(match_id)
    except Exception as e:
        
        logError(f"Error in get_match: ", e, "get_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def update_match(match_id: int, match: Match):
    """Updates a match with the provided data.
    
    Params:
        match_id (int): The ID of the match to update.
        Example:
            1
        match (Match): The match object containing the updated data.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "resume_id": 1,
            "status": "PENDING"
        }

    Returns:
        Match: The match object updated.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "resume_id": 1,
            "status": "PENDING"
        }

    Raises:
        HTTPException: If an error occurs while updating the match.
    """
    try:
        log(f"Updating match with ID: {match_id}", "update_match")
        if not Validation.validate_match(match):
            raise HTTPException(status_code=400, detail="Invalid match data.")
        
        match.match_id = match_id
        MatchDatabase.update_match(match)
        return match
    except HTTPException as e:
        
        logError(f"Validation error in update_match: ", e, "update_match")
        raise e
    except Exception as e:
        
        logError(f"Error in update_match: ", e, "update_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/matches/{match_id}", tags=["Matches"])
async def delete_match(match_id: int):
    """Deletes a match with the provided ID.
    
    Params:
        match_id (int): The ID of the match to delete.
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
        MatchDatabase.delete_match(match_id)
        return {"message": "Match deleted successfully."}
    except Exception as e:
        
        logError(f"Error in delete_match: ", e, "delete_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/matches/uid", tags=["Matches"])
async def get_matches_by_uid(request: GetMatchesRequest):
    """Retrieves all matches for a user with the provided UID.
    
    Params:
        request (GetMatchesRequest): The request object containing the UID of the user.
        Example:
        {
            "uid": "12345"
        }

    Returns:
        List[Match]: A list of all matches for the user.
        Example:
        [
            {
                "uid": "12345",
                "job_id": 1,
                "resume_id": 1,
                "status": "PENDING"
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving the matches.
    """
    try:
        log(f"Retrieving matches for user UID: {request.uid}", "get_matches_by_uid")
        matches = MatchDatabase.get_all_matches()
        user_matches = [match for match in matches if match.uid == request.uid]
        return [MatchFactory.to_json(match) for match in user_matches]
    except Exception as e:
        
        logError(f"Error in get_matches_by_uid: ", e, "get_matches_by_uid")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/", response_model=List[Match], tags=["Matches"])
async def get_all_matches():
    """Retrieves all matches.
    
    Params:
        None
        
    Returns:
        List[Match]: A list of all matches.
        Example:
        [
            {
                "uid": "12345",
                "job_id": 1,
                "resume_id": 1,
                "status": "PENDING"
            }
        ]

    Raises:
        HTTPException: If an error occurs while retrieving all matches.
    """
    try:
        log("Retrieving all matches", "get_all_matches")
        return MatchDatabase.get_all_matches()
    except Exception as e:
        
        logError(f"Error in get_all_matches: ", e, "get_all_matches")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/feedback/", response_model=Feedback, tags=["Feedback"])
async def create_feedback(feedback: Feedback):
    """Creates a new feedback with the provided data.
    
    Params:
        feedback (Feedback): The feedback object containing the feedback data.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "rating": 5,
            "comment": "Feedback comment."
        }

    Returns:
        Feedback: The feedback object created.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "rating": 5,
            "comment": "Feedback comment."
        }

    Raises:
        HTTPException: If an error occurs while creating the feedback.
    """
    try:
        log("Creating a new feedback", "create_feedback")
        if not Validation.validate_feedback(feedback):
            raise HTTPException(status_code=400, detail="Invalid feedback data.")
        
        FeedbackDatabase.create_feedback(feedback)
        return feedback
    except HTTPException as e:
        
        logError(f"Validation error in create_feedback: ", e, "create_feedback")
        raise e
    except Exception as e:
        
        logError(f"Error in create_feedback: ", e, "create_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def get_feedback(feedback_id: int):
    """Retrieves a feedback with the provided ID.
    
    Params:
        feedback_id (int): The ID of the feedback to retrieve.
        Example:
            1
            
    Returns:
        Feedback: The feedback object retrieved.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "rating": 5,
            "comment": "Feedback comment."
        }

    Raises:
        HTTPException: If an error occurs while retrieving the feedback.
    """
    try:
        log(f"Retrieving feedback with ID: {feedback_id}", "get_feedback")
        return FeedbackDatabase.get_feedback(feedback_id)
    except Exception as e:
        
        logError(f"Error in get_feedback: ", e, "get_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def update_feedback(feedback_id: int, feedback: Feedback):
    """Updates a feedback with the provided data.
    
    Params:
        feedback_id (int): The ID of the feedback to update.
        Example:
            1
        feedback (Feedback): The feedback object containing the updated data.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "rating": 5,
            "comment": "Feedback comment."
        }

    Returns:
        Feedback: The feedback object updated.
        Example:
        {
            "uid": "12345",
            "job_id": 1,
            "rating": 5,
            "comment": "Feedback comment."
        }

    Raises:
        HTTPException: If an error occurs while updating the feedback.
    """
    try:
        log(f"Updating feedback with ID: {feedback_id}", "update_feedback")
        if not Validation.validate_feedback(feedback):
            raise HTTPException(status_code=400, detail="Invalid feedback data.")
        
        feedback.feedback_id = feedback_id
        FeedbackDatabase.update_feedback(feedback)
        return feedback
    except HTTPException as e:
        
        logError(f"Validation error in update_feedback: ", e, "update_feedback")
        raise e
    except Exception as e:
        
        logError(f"Error in update_feedback: ", e, "update_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/feedback/{feedback_id}", tags=["Feedback"])
async def delete_feedback(feedback_id: int):
    """Deletes a feedback with the provided ID.
    
    Params:
        feedback_id (int): The ID of the feedback to delete.
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
        FeedbackDatabase.delete_feedback(feedback_id)
        return {"message": "Feedback deleted successfully."}
    except Exception as e:
        
        logError(f"Error in delete_feedback: ", e, "delete_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/", response_model=List[Feedback], tags=["Feedback"])
async def get_all_feedbacks():
    """ Retrieves all feedbacks.
    
    Params:
        None
    
    Returns:
        List[Feedback]: A list of all feedbacks.
        Example:
        [
            {
                "uid": "12345",
                "job_id": 1,
                "rating": 5,
                "comment": "Feedback comment."
            }
        ]
    
    Raises:
        HTTPException: If an error occurs while retrieving all feedbacks.
    """
    try:
        log("Retrieving all feedbacks", "get_all_feedbacks")
        return FeedbackDatabase.get_all_feedbacks()
    except Exception as e:
        
        logError(f"Error in get_all_feedbacks: ", e, "get_all_feedbacks")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/logs/download", tags=["Logs"])
async def download_logs():
    """Downloads the log files as a zip archive.
    
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
async def compress_logs():
    """Compresses the log files into a zip archive.

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

@app.post("/grade/job", tags=["Grading"])
async def grade_job(request: GradeJobRequest):
    """ Grades resumes for a job.
    
    Params:
        request (GradeJobRequest): The request object containing the job ID.
        Example:
        {
            "job_id": 1
        }
    
    Returns:
        List[Match]: A list of matches for the job.
        Example:
        [
            {
                "uid": "12345",
                "job_id": 1,
                "resume_id": 1,
                "status": "PENDING"
            }
        ]
    
    Raises:
        HTTPException: If an error occurs while grading the job.
    """
    try:
        log("Grading job", "grade_job")
        matches = GradingService.grade_resumes_for_job(request.job_id)
        return matches
    except Exception as e:
        
        logError(f"Error in grade_job: ", e, "grade_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    user = User(
        uid="uid",
        name=Name(first_name="Chia-Hsun", last_name="Hsieh"),
        is_admin=False,
        is_owner=False,
        phone_number="00-0000000000",
        dob="14062024",
        email="testing30@gmail.com"
    )
    create_user(CreateUserRequest)
