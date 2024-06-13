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


def logError(message, func):
    Logger.logMain(message, func, "ERROR")


@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint for the API. Returns a welcome message and information about the API.
    
    Params:
        None
        
    Returns:
        dict: A dictionary containing the welcome message and API information.
        Example:
        {
            "message": "Welcome to the API!",
            "author": "BugSlayerz.HarijotSingh",
            "description": "This is a FastAPI project backend for a job matching system.",
            "Contact us": "sidhuharijot@gmail.com",
            "version": "3.0"
        }
        
    Raises:
        HTTPException: If an error occurs while accessing the root endpoint.
    """
    try:
        log("Accessing root endpoint", "read_root")
        return {"message": "Welcome to the API!", "author": "BugSlayerz.HarijotSingh", "description": "This is a FastAPI project backend for a job matching system.", "Contact us": "sidhuharijot@gmail.com", "version": "3.0"}
    except Exception as e:
        logError(f"Error in root endpoint: {str(e)}", "read_root")
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
            "dob": "DDMMYYYY",
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
            "dob": "DDMMYYYY",
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
            is_owner=request.is_owner,
            is_admin=request.is_admin,
            phone_number=request.phone_number,
            email=request.email
        )
        
        if not Validation.validate_user(user):
            raise HTTPException(status_code=400, detail="Invalid user data.")
        
        UserDatabase.create_user(user)
        return user
    except HTTPException as e:
        logError(f"Validation error in create_user: {str(e)}", "create_user")
        raise e
    except Exception as e:
        logError(f"Error in create_user: {str(e)}", "create_user")
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
            "dob": "DDMMYYYY",
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
        logError(f"Error in get_user: {str(e)}", "get_user")
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
            "dob": "DDMMYYYY",
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
            "dob": "DDMMYYYY",
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
        logError(f"Validation error in update_user: {str(e)}", "update_user")
        raise e
    except Exception as e:
        logError(f"Error in update_user: {str(e)}", "update_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/users/{uid}", tags=["Users"])
async def delete_user(uid: str):
    """Deletes a user with the provided UID.

    Params:
        uid (str): The UID of the user to delete.
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
        UserDatabase.delete_user(uid)
        return {"message": "User deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_user: {str(e)}", "delete_user")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_all_users(auth_uid: str):
    try:
        log("Retrieving all users", "get_all_users")
        if not (Authorize.checkAuth(auth_uid, "ADMIN") or Authorize.checkAuth(auth_uid, "OWNER")):
            raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
        
        return UserDatabase.get_all_users()
    except HTTPException as e:
        logError(f"Authorization error in get_all_users: {str(e)}", "get_all_users")
        raise e
    except Exception as e:
        logError(f"Error in get_all_users: {str(e)}", "get_all_users")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/users/update_privileges", tags=["Users"])
async def update_user_privileges(request: UpdateUserPrivilegesRequest):
    """Updates the privileges of a user with the provided data.
    
    Params:
        request (UpdateUserPrivilegesRequest): The request object containing the updated user privileges.
        Example:
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
        logError(f"Authorization or validation error in update_user_privileges: {str(e)}", "update_user_privileges")
        raise e
    except Exception as e:
        logError(f"Error in update_user_privileges: {str(e)}", "update_user_privileges")
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
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
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
        logError(f"Validation error in create_resume: {str(e)}", "create_resume")
        raise e
    except Exception as e:
        logError(f"Error in create_resume: {str(e)}", "create_resume")
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
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
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
        logError(f"Error in get_resume: {str(e)}", "get_resume")
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
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
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
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
                    "title": "Software Engineer",
                    "company_name": "Company",
                    "description": "Description of the experience."
                }
            ],
            "education": [
                {
                    "start_date": "DDMMYYYY",
                    "end_date": "DDMMYYYY",
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
        logError(f"Validation error in update_resume: {str(e)}", "update_resume")
        raise e
    except Exception as e:
        logError(f"Error in update_resume: {str(e)}", "update_resume")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/resumes/{uid}", tags=["Resumes"])
async def delete_resume(uid: str):
    """Deletes a resume with the provided UID.

    Params:
        uid (str): The UID of the resume to delete.
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
        ResumeDatabase.delete_resume(uid)
        return {"message": "Resume deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_resume: {str(e)}", "delete_resume")
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
                        "start_date": "DDMMYYYY",
                        "end_date": "DDMMYYYY",
                        "title": "Software Engineer",
                        "company_name": "Company",
                        "description": "Description of the experience."
                    }
                ],
                "education": [
                    {
                        "start_date": "DDMMYYYY",
                        "end_date": "DDMMYYYY",
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
        logError(f"Error in get_all_resumes: {str(e)}", "get_all_resumes")
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
            "application_deadline": "DDMMYYYY",
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
        logError(f"Validation error in create_job: {str(e)}", "create_job")
        raise e
    except Exception as e:
        logError(f"Error in create_job: {str(e)}", "create_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def get_job(job_id: int):
    """Retrieves a job with the provided ID.
    
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
            "application_deadline": "DDMMYYYY",
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
        logError(f"Error in get_job: {str(e)}", "get_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def update_job(job_id: int, request: UpdateJobRequest):
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
        logError(f"Validation error in update_job: {str(e)}", "update_job")
        raise e
    except Exception as e:
        logError(f"Error in update_job: {str(e)}", "update_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: int):
    try:
        log(f"Deleting job with ID: {job_id}", "delete_job")
        JobDatabase.delete_job(job_id)
        return {"message": "Job deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_job: {str(e)}", "delete_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/jobs/", response_model=List[Job], tags=["Jobs"])
async def get_all_jobs():
    try:
        log("Retrieving all jobs", "get_all_jobs")
        return JobDatabase.get_all_jobs()
    except Exception as e:
        logError(f"Error in get_all_jobs: {str(e)}", "get_all_jobs")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/matches/", response_model=Match, tags=["Matches"])
async def create_match(match: Match):
    try:
        log("Creating a new match", "create_match")
        if not Validation.validate_match(match):
            raise HTTPException(status_code=400, detail="Invalid match data.")
        
        MatchDatabase.create_match(match)
        return match
    except HTTPException as e:
        logError(f"Validation error in create_match: {str(e)}", "create_match")
        raise e
    except Exception as e:
        logError(f"Error in create_match: {str(e)}", "create_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def get_match(match_id: int):
    try:
        log(f"Retrieving match with ID: {match_id}", "get_match")
        return MatchDatabase.get_match(match_id)
    except Exception as e:
        logError(f"Error in get_match: {str(e)}", "get_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def update_match(match_id: int, match: Match):
    try:
        log(f"Updating match with ID: {match_id}", "update_match")
        if not Validation.validate_match(match):
            raise HTTPException(status_code=400, detail="Invalid match data.")
        
        match.match_id = match_id
        MatchDatabase.update_match(match)
        return match
    except HTTPException as e:
        logError(f"Validation error in update_match: {str(e)}", "update_match")
        raise e
    except Exception as e:
        logError(f"Error in update_match: {str(e)}", "update_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/matches/{match_id}", tags=["Matches"])
async def delete_match(match_id: int):
    try:
        log(f"Deleting match with ID: {match_id}", "delete_match")
        MatchDatabase.delete_match(match_id)
        return {"message": "Match deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_match: {str(e)}", "delete_match")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/matches/uid", tags=["Matches"])
async def get_matches_by_uid(request: GetMatchesRequest):
    try:
        log(f"Retrieving matches for user UID: {request.uid}", "get_matches_by_uid")
        matches = MatchDatabase.get_all_matches()
        user_matches = [match for match in matches if match.uid == request.uid]
        return [MatchFactory.to_json(match) for match in user_matches]
    except Exception as e:
        logError(f"Error in get_matches_by_uid: {str(e)}", "get_matches_by_uid")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/matches/", response_model=List[Match], tags=["Matches"])
async def get_all_matches():
    try:
        log("Retrieving all matches", "get_all_matches")
        return MatchDatabase.get_all_matches()
    except Exception as e:
        logError(f"Error in get_all_matches: {str(e)}", "get_all_matches")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/feedback/", response_model=Feedback, tags=["Feedback"])
async def create_feedback(feedback: Feedback):
    try:
        log("Creating a new feedback", "create_feedback")
        if not Validation.validate_feedback(feedback):
            raise HTTPException(status_code=400, detail="Invalid feedback data.")
        
        FeedbackDatabase.create_feedback(feedback)
        return feedback
    except HTTPException as e:
        logError(f"Validation error in create_feedback: {str(e)}", "create_feedback")
        raise e
    except Exception as e:
        logError(f"Error in create_feedback: {str(e)}", "create_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def get_feedback(feedback_id: int):
    try:
        log(f"Retrieving feedback with ID: {feedback_id}", "get_feedback")
        return FeedbackDatabase.get_feedback(feedback_id)
    except Exception as e:
        logError(f"Error in get_feedback: {str(e)}", "get_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def update_feedback(feedback_id: int, feedback: Feedback):
    try:
        log(f"Updating feedback with ID: {feedback_id}", "update_feedback")
        if not Validation.validate_feedback(feedback):
            raise HTTPException(status_code=400, detail="Invalid feedback data.")
        
        feedback.feedback_id = feedback_id
        FeedbackDatabase.update_feedback(feedback)
        return feedback
    except HTTPException as e:
        logError(f"Validation error in update_feedback: {str(e)}", "update_feedback")
        raise e
    except Exception as e:
        logError(f"Error in update_feedback: {str(e)}", "update_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/feedback/{feedback_id}", tags=["Feedback"])
async def delete_feedback(feedback_id: int):
    try:
        log(f"Deleting feedback with ID: {feedback_id}", "delete_feedback")
        FeedbackDatabase.delete_feedback(feedback_id)
        return {"message": "Feedback deleted successfully."}
    except Exception as e:
        logError(f"Error in delete_feedback: {str(e)}", "delete_feedback")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/feedback/", response_model=List[Feedback], tags=["Feedback"])
async def get_all_feedbacks():
    try:
        log("Retrieving all feedbacks", "get_all_feedbacks")
        return FeedbackDatabase.get_all_feedbacks()
    except Exception as e:
        logError(f"Error in get_all_feedbacks: {str(e)}", "get_all_feedbacks")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/logs/download", tags=["Logs"])
async def download_logs():
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
        logError(f"Error in download_logs: {str(e)}", "download_logs")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Clean up decompressed log files
        for file in log_folder.glob("*.txt"):
            if file.name != datetime.datetime.now().strftime("logs%d-%m-%Y.txt"):
                file.unlink()

@app.post("/logs/compress", tags=["Logs"])
async def compress_logs():
    try:
        log("Compressing logs", "compress_logs")
        Logger.compressLogs()
        return {"message": "Logs compressed successfully."}
    except Exception as e:
        logError(f"Error in compress_logs: {str(e)}", "compress_logs")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/grade/job", tags=["Grading"])
async def grade_job(request: GradeJobRequest):
    try:
        log("Grading job", "grade_job")
        matches = GradingService.grade_resumes_for_job(request.job_id)
        return [MatchFactory.to_json(match) for match in matches]
    except Exception as e:
        logError(f"Error in grade_job: {str(e)}", "grade_job")
        raise HTTPException(status_code=500, detail="Internal Server Error")

