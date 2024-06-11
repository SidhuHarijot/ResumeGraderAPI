from pydantic import BaseModel, Field
from typing import List, Optional

class UpdateUserPrivilegesRequest(BaseModel):
    target_uid: str = Field(..., description="UID of the user whose privileges are being updated.")
    is_admin: Optional[bool] = Field(None, description="Whether the user should be an admin.")
    is_owner: Optional[bool] = Field(None, description="Whether the user should be an owner.")
    auth_uid: str = Field(..., description="UID of the admin or owner authorizing the action.")
    
class CreateUserRequest(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    dob: str = Field(..., description="Date of birth of the user in DDMMYYYY format.")
    is_owner: Optional[bool] = Field(False, description="Whether the user is an owner.")
    is_admin: Optional[bool] = Field(False, description="Whether the user is an admin.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")

class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = Field(None, description="First name of the user.")
    last_name: Optional[str] = Field(None, description="Last name of the user.")
    dob: Optional[str] = Field(None, description="Date of birth of the user in DDMMYYYY format.")
    phone_number: Optional[str] = Field(None, description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: Optional[str] = Field(None, description="Email of the user.")
    is_owner: Optional[bool] = Field(None, description="Whether the user is an owner.")
    is_admin: Optional[bool] = Field(None, description="Whether the user is an admin.")

class CreateJobRequest(BaseModel):
    title: str = Field(..., description="Title of the job.")
    company: str = Field(..., description="Company name.")
    description: str = Field(..., description="Description of the job.")
    required_skills: List[str] = Field(..., description="Required skills for the job.")
    application_deadline: str = Field(..., description="Deadline for job applications in DDMMYYYY format.")
    location: str = Field(..., description="Location of the job.")
    salary: float = Field(..., description="Salary for the job.")
    job_type: str = Field(..., description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: Optional[bool] = Field(True, description="Status of the job, whether it is active or not.")
    
class UpdateJobRequest(BaseModel):
    title: Optional[str] = Field(None, description="Title of the job.")
    company: Optional[str] = Field(None, description="Company name.")
    description: Optional[str] = Field(None, description="Description of the job.")
    required_skills: Optional[List[str]] = Field(None, description="Required skills for the job.")
    application_deadline: Optional[str] = Field(None, description="Deadline for job applications in DDMMYYYY format.")
    location: Optional[str] = Field(None, description="Location of the job.")
    salary: Optional[float] = Field(None, description="Salary for the job.")
    job_type: Optional[str] = Field(None, description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: Optional[bool] = Field(None, description="Status of the job, whether it is active or not.")

class GradeJobRequest(BaseModel):
    job_id: int

class GetMatchesRequest(BaseModel):
    uid: str
