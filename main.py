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

# Initialize database connection
Database.initialize()


@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message.
        Example:
        {
            "message": "Welcome to the API!"
        }
    """
    return {"message": "Welcome to the API!", "author": "BugSlayerz.HarijotSingh", "description": "This is a FastAPI project backend for a job matching system.", "Contact us": "sidhuharijot@gmail.com", "version": "3.0"}


@app.post("/users/", response_model=User, tags=["Users"])
async def create_user(request: CreateUserRequest):
    """
    Create a new user.

    Args:
        request (CreateUserRequest): User data.
        Example:
        {
            "uid": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "01012000",
            "is_owner": False,
            "is_admin": False,
            "phone_number": "01-1234567890",
            "email": "john.doe@example.com"
        }

    Returns:
        User: User object containing the created user data.
        Example:
        {
            "uid": "user123",
            "name": {"first_name": "John", "last_name": "Doe"},
            "dob": {"day": 1, "month": 1, "year": 2000},
            "is_owner": False,
            "is_admin": False,
            "phone_number": "01-1234567890",
            "email": "john.doe@example.com"
        }

    Raises:
        HTTPException: If an error occurs during user creation.
    """
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

@app.get("/users/{uid}", response_model=User, tags=["Users"])
async def get_user(uid: str):
    """
    Retrieve a user by UID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "user123"
        }

    Returns:
        User: User object containing the user data.
        Example:
        {
            "uid": "user123",
            "name": {"first_name": "John", "last_name": "Doe"},
            "dob": {"day": 1, "month": 1, "year": 2000},
            "is_owner": False,
            "is_admin": False,
            "phone_number": "01-1234567890",
            "email": "john.doe@example.com"
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return UserDatabase.get_user(uid)

@app.put("/users/{uid}", response_model=User, tags=["Users"])
async def update_user(uid: str, request: UpdateUserRequest):
    """
    Update a user by UID.

    Args:
        uid (str): User ID.
        request (UpdateUserRequest): Updated user data.
        Example:
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "dob": "02022000",
            "phone_number": "01-0987654321",
            "email": "jane.doe@example.com",
            "is_owner": True,
            "is_admin": True
        }

    Returns:
        User: User object containing the updated user data.
        Example:
        {
            "uid": "user123",
            "name": {"first_name": "Jane", "last_name": "Doe"},
            "dob": {"day": 2, "month": 2, "year": 2000},
            "is_owner": True,
            "is_admin": True,
            "phone_number": "01-0987654321",
            "email": "jane.doe@example.com"
        }

    Raises:
        HTTPException: If an error occurs during user update.
    """
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

@app.delete("/users/{uid}", tags=["Users"])
async def delete_user(uid: str):
    """
    Delete a user by UID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "user123"
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "User deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs during user deletion.
    """
    UserDatabase.delete_user(uid)
    return {"message": "User deleted successfully."}

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_all_users(auth_uid: str):
    """
    Retrieve all users. This action is allowed only for admins and owners.

    Args:
        auth_uid (str): UID of the admin or owner authorizing the action.
        Example:
        {
            "auth_uid": "admin123"
        }

    Returns:
        List[User]: List of all user objects.
        Example:
        [
            {
                "uid": "user123",
                "name": {"first_name": "John", "last_name": "Doe"},
                "dob": {"day": 1, "month": 1, "year": 2000},
                "is_owner": False,
                "is_admin": False,
                "phone_number": "01-1234567890",
                "email": "john.doe@example.com"
            },
            ...
        ]

    Raises:
        HTTPException: If the requester is not authorized.
    """
    if not (Authorize.checkAuth(auth_uid, "ADMIN") or Authorize.checkAuth(auth_uid, "OWNER")):
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    
    return UserDatabase.get_all_users()

@app.post("/users/update_privileges", tags=["Users"])
async def update_user_privileges(request: UpdateUserPrivilegesRequest):
    """
    Update user privileges to admin or owner. This action is allowed only for admins and owners.

    Args:
        request (UpdateUserPrivilegesRequest): Request data.
        Example:
        {
            "target_uid": "user123",
            "is_admin": True,
            "is_owner": False,
            "auth_uid": "admin123"
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "User privileges updated successfully."
        }

    Raises:
        HTTPException: If the requester is not authorized or if an error occurs during update.
    """
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

@app.post("/resumes/", response_model=Resume, tags=["Resumes"])
async def create_resume(file: UploadFile = File(None), resume_text: Optional[str] = None):
    """
    Create a new resume from a file or text.

    Args:
        file (UploadFile, optional): Resume file.
        resume_text (str, optional): Resume text.
        Example:
        {
            "file": "resume.pdf",
            "resume_text": "Resume content as a string"
        }

    Returns:
        Resume: Resume object containing the created resume data.
        Example:
        {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [{"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company", "description": "Description"}],
            "education": [{"start_date": "01012018", "end_date": "01012022", "institution": "University", "course_name": "CS"}]
        }

    Raises:
        HTTPException: If an error occurs during resume creation.
    """
    resume = ResumeService.process_resume(file, resume_text)
    
    if not Validation.validate_resume(resume):
        raise HTTPException(status_code=400, detail="Invalid resume data.")
    
    ResumeDatabase.create_resume(resume)
    return resume

@app.get("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def get_resume(uid: str):
    """
    Retrieve a resume by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "user123"
        }

    Returns:
        Resume: Resume object containing the resume data.
        Example:
        {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [{"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company", "description": "Description"}],
            "education": [{"start_date": "01012018", "end_date": "01012022", "institution": "University", "course_name": "CS"}]
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return ResumeDatabase.get_resume(uid)

@app.put("/resumes/{uid}", response_model=Resume, tags=["Resumes"])
async def update_resume(uid: str, resume: Resume):
    """
    Update a resume by user ID.

    Args:
        uid (str): User ID.
        resume (Resume): Updated resume data.
        Example:
        {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [{"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company", "description": "Description"}],
            "education": [{"start_date": "01012018", "end_date": "01012022", "institution": "University", "course_name": "CS"}]
        }

    Returns:
        Resume: Resume object containing the updated resume data.
        Example:
        {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [{"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company", "description": "Description"}],
            "education": [{"start_date": "01012018", "end_date": "01012022", "institution": "University", "course_name": "CS"}]
        }

    Raises:
        HTTPException: If an error occurs during resume update.
    """
    if not Validation.validate_resume(resume):
        raise HTTPException(status_code=400, detail="Invalid resume data.")
    
    resume.uid = uid
    ResumeDatabase.update_resume(resume)
    return resume

@app.delete("/resumes/{uid}", tags=["Resumes"])
async def delete_resume(uid: str):
    """
    Delete a resume by user ID.

    Args:
        uid (str): User ID.
        Example:
        {
            "uid": "user123"
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "Resume deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs during resume deletion.
    """
    ResumeDatabase.delete_resume(uid)
    return {"message": "Resume deleted successfully."}

@app.get("/resumes/", response_model=List[Resume], tags=["Resumes"])
async def get_all_resumes():
    """
    Retrieve all resumes.

    Returns:
        List[Resume]: List of all resume objects.
        Example:
        [
            {
                "uid": "user123",
                "skills": ["Python", "Java"],
                "experience": [{"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company", "description": "Description"}],
                "education": [{"start_date": "01012018", "end_date": "01012022", "institution": "University", "course_name": "CS"}]
            },
            ...
        ]

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return ResumeDatabase.get_all_resumes()

@app.post("/jobs/", response_model=Job, tags=["Jobs"])
async def create_job(file: UploadFile = File(None), job_description_text: Optional[str] = None):
    """
    Create a new job from a file or text.

    Args:
        file (UploadFile, optional): Job description file.
        job_description_text (str, optional): Job description text.
        Example:
        {
            "file": "job_description.pdf",
            "job_description_text": "Job description content as a string"
        }

    Returns:
        Job: Job object containing the created job data.
        Example:
        {
            "job_id": 1,
            "title": "Job Title",
            "company": "Company Name",
            "description": "Job Description",
            "required_skills": ["skill1", "skill2"],
            "application_deadline": "2024-12-31",
            "location": "Location",
            "salary": 100000.00,
            "job_type": "FULL",
            "active": True
        }

    Raises:
        HTTPException: If an error occurs during job creation.
    """
    job = JobService.process_job_description(file, job_description_text)
    
    if not Validation.validate_job(job):
        raise HTTPException(status_code=400, detail="Invalid job data.")
    
    JobDatabase.create_job(job)
    return job

@app.get("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def get_job(job_id: int):
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
            "title": "Job Title",
            "company": "Company Name",
            "description": "Job Description",
            "required_skills": ["skill1", "skill2"],
            "application_deadline": "2024-12-31",
            "location": "Location",
            "salary": 100000.00,
            "job_type": "FULL",
            "active": True
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return JobDatabase.get_job(job_id)

@app.put("/jobs/{job_id}", response_model=Job, tags=["Jobs"])
async def update_job(job_id: int, request: UpdateJobRequest):
    """
    Update a job by job ID.

    Args:
        job_id (int): Job ID.
        request (UpdateJobRequest): Updated job data.
        Example:
        {
            "title": "Updated Job Title",
            "company": "Updated Company Name",
            "description": "Updated Job Description",
            "required_skills": ["skill1", "skill2"],
            "application_deadline": "2024-12-31",
            "location": "Updated Location",
            "salary": 120000.00,
            "job_type": "FULL",
            "active": False
        }

    Returns:
        Job: Job object containing the updated job data.
        Example:
        {
            "job_id": 1,
            "title": "Updated Job Title",
            "company": "Updated Company Name",
            "description": "Updated Job Description",
            "required_skills": ["skill1", "skill2"],
            "application_deadline": "2024-12-31",
            "location": "Updated Location",
            "salary": 120000.00,
            "job_type": "FULL",
            "active": False
        }

    Raises:
        HTTPException: If an error occurs during job update.
    """
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

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: int):
    """
    Delete a job by job ID.

    Args:
        job_id (int): Job ID.
        Example:
        {
            "job_id": 1
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "Job deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs during job deletion.
    """
    JobDatabase.delete_job(job_id)
    return {"message": "Job deleted successfully."}

@app.get("/jobs/", response_model=List[Job], tags=["Jobs"])
async def get_all_jobs():
    """
    Retrieve all jobs.

    Returns:
        List[Job]: List of all job objects.
        Example:
        [
            {
                "job_id": 1,
                "title": "Job Title",
                "company": "Company Name",
                "description": "Job Description",
                "required_skills": ["skill1", "skill2"],
                "application_deadline": "2024-12-31",
                "location": "Location",
                "salary": 100000.00,
                "job_type": "FULL",
                "active": True
            },
            ...
        ]

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return JobDatabase.get_all_jobs()

@app.post("/matches/", response_model=Match, tags=["Matches"])
async def create_match(match: Match):
    """
    Create a new match.

    Args:
        match (Match): Match data.
        Example:
        {
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85.0,
            "selected_skills": ["skill1", "skill2"]
        }

    Returns:
        Match: Match object containing the created match data.
        Example:
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85.0,
            "selected_skills": ["skill1", "skill2"]
        }

    Raises:
        HTTPException: If an error occurs during match creation.
    """
    if not Validation.validate_match(match):
        raise HTTPException(status_code=400, detail="Invalid match data.")
    
    MatchDatabase.create_match(match)
    return match

@app.get("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def get_match(match_id: int):
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
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85.0,
            "selected_skills": ["skill1", "skill2"]
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return MatchDatabase.get_match(match_id)

@app.put("/matches/{match_id}", response_model=Match, tags=["Matches"])
async def update_match(match_id: int, match: Match):
    """
    Update a match by match ID.

    Args:
        match_id (int): Match ID.
        match (Match): Updated match data.
        Example:
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85.0,
            "selected_skills": ["skill1", "skill2"]
        }

    Returns:
        Match: Match object containing the updated match data.
        Example:
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85.0,
            "selected_skills": ["skill1", "skill2"]
        }

    Raises:
        HTTPException: If an error occurs during match update.
    """
    if not Validation.validate_match(match):
        raise HTTPException(status_code=400, detail="Invalid match data.")
    
    match.match_id = match_id
    MatchDatabase.update_match(match)
    return match

@app.delete("/matches/{match_id}", tags=["Matches"])
async def delete_match(match_id: int):
    """
    Delete a match by match ID.

    Args:
        match_id (int): Match ID.
        Example:
        {
            "match_id": 1
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "Match deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs during match deletion.
    """
    MatchDatabase.delete_match(match_id)
    return {"message": "Match deleted successfully."}


@app.post("/matches/uid", tags=["Matches"])
async def get_matches_by_uid(request: GetMatchesRequest):
    """
    Get matches by user ID.

    Args:
        request (GetMatchesRequest): Request object containing the user ID.
        Example:
        {
            "uid": "user123"
        }

    Returns:
        List[Match]: List of Match objects for the specified user.
        Example:
        [
            {
                "match_id": 1,
                "uid": "user123",
                "job_id": 1,
                "status": "Application received",
                "status_code": 100,
                "grade": 85,
                "selected_skills": ["skill1", "skill2"]
            }
        ]

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    try:
        matches = MatchDatabase.get_all_matches()
        user_matches = [match for match in matches if match.uid == request.uid]
        return [MatchFactory.to_json(match) for match in user_matches]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving matches: {str(e)}")


@app.get("/matches/", response_model=List[Match], tags=["Matches"])
async def get_all_matches():
    """
    Retrieve all matches.

    Returns:
        List[Match]: List of all match objects.
        Example:
        [
            {
                "match_id": 1,
                "uid": "user123",
                "job_id": 1,
                "status": "Application received",
                "status_code": 100,
                "grade": 85.0,
                "selected_skills": ["skill1", "skill2"]
            },
            ...
        ]

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return MatchDatabase.get_all_matches()

@app.post("/feedback/", response_model=Feedback, tags=["Feedback"])
async def create_feedback(feedback: Feedback):
    """
    Create a new feedback.

    Args:
        feedback (Feedback): Feedback data.
        Example:
        {
            "match_id": 1,
            "feedback_text": "Great match!"
        }

    Returns:
        Feedback: Feedback object containing the created feedback data.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great match!"
        }

    Raises:
        HTTPException: If an error occurs during feedback creation.
    """
    if not Validation.validate_feedback(feedback):
        raise HTTPException(status_code=400, detail="Invalid feedback data.")
    
    FeedbackDatabase.create_feedback(feedback)
    return feedback

@app.get("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def get_feedback(feedback_id: int):
    """
    Retrieve a feedback by feedback ID.

    Args:
        feedback_id (int): Feedback ID.
        Example:
        {
            "feedback_id": 1
        }

    Returns:
        Feedback: Feedback object containing the feedback data.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great match!"
        }

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return FeedbackDatabase.get_feedback(feedback_id)

@app.put("/feedback/{feedback_id}", response_model=Feedback, tags=["Feedback"])
async def update_feedback(feedback_id: int, feedback: Feedback):
    """
    Update a feedback by feedback ID.

    Args:
        feedback_id (int): Feedback ID.
        feedback (Feedback): Updated feedback data.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great match!"
        }

    Returns:
        Feedback: Feedback object containing the updated feedback data.
        Example:
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great match!"
        }

    Raises:
        HTTPException: If an error occurs during feedback update.
    """
    if not Validation.validate_feedback(feedback):
        raise HTTPException(status_code=400, detail="Invalid feedback data.")
    
    feedback.feedback_id = feedback_id
    FeedbackDatabase.update_feedback(feedback)
    return feedback

@app.delete("/feedback/{feedback_id}", tags=["Feedback"])
async def delete_feedback(feedback_id: int):
    """
    Delete a feedback by feedback ID.

    Args:
        feedback_id (int): Feedback ID.
        Example:
        {
            "feedback_id": 1
        }

    Returns:
        dict: Success message.
        Example:
        {
            "message": "Feedback deleted successfully."
        }

    Raises:
        HTTPException: If an error occurs during feedback deletion.
    """
    FeedbackDatabase.delete_feedback(feedback_id)
    return {"message": "Feedback deleted successfully."}

@app.get("/feedback/", response_model=List[Feedback], tags=["Feedback"])
async def get_all_feedbacks():
    """
    Retrieve all feedbacks.

    Returns:
        List[Feedback]: List of all feedback objects.
        Example:
        [
            {
                "feedback_id": 1,
                "match_id": 1,
                "feedback_text": "Great match!"
            },
            ...
        ]

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    return FeedbackDatabase.get_all_feedbacks()

@app.get("/logs/download", tags=["Logs"])
async def download_logs():
    """
    Download logs.

    Returns:
        FileResponse: File containing the logs.

    Raises:
        HTTPException: If an error occurs during log retrieval.
    """
    log_folder = Path(Logger.logFolder)
    decompressed_folder = Path(Logger.decompressed)

    try:
        # Ensure logs are decompressed
        Logger.decompressLogs()

        # Create a zip of the logs
        zip_path = log_folder / "logs.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), 'zip', decompressed_folder)
        Logger.clearDecompressedLogs()
        return FileResponse(str(zip_path), filename="logs.zip", media_type='application/zip')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving logs: {str(e)}")
    finally:
        # Clean up decompressed log files
        for file in log_folder.glob("*.txt"):
            if file.name != datetime.datetime.now().strftime("logs%d-%m-%Y.txt"):
                file.unlink()

@app.post("/logs/compress", tags=["Logs"])
async def compress_logs():
    """
    Compress logs.

    Returns:
        dict: Success message.
        Example:
        {
            "message": "Logs compressed successfully."
        }

    Raises:
        HTTPException: If an error occurs during log compression.
    """
    try:
        Logger.compressLogs()
        return {"message": "Logs compressed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while compressing logs: {str(e)}")


@app.post("/grade/job", tags=["Grading"])
async def grade_job(request: GradeJobRequest):
    """
    Grade all resumes attached to a job description.

    Args:
        request (GradeJobRequest): Request object containing the job ID.
        Example:
        {
            "job_id": 1
        }

    Returns:
        List[Match]: List of Match objects containing the graded matches.
        Example:
        [
            {
                "match_id": 1,
                "uid": "user123",
                "job_id": 1,
                "status": "graded",
                "status_code": 85,
                "grade": 85,
                "selected_skills": ["skill1", "skill2"]
            }
        ]

    Raises:
        HTTPException: If an error occurs during the grading process.
    """
    try:
        matches = GradingService.grade_resumes_for_job(request.job_id)
        return [MatchFactory.to_json(match) for match in matches]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while grading job: {str(e)}")

