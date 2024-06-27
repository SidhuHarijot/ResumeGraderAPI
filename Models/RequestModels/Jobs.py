from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import List, Optional
 

class Create(BaseModel):
    title: Optional[str] = Field(None, description="Title of the job.")
    company: Optional[str] = Field(None, description="Company name.")
    description: Optional[str] = Field(None, description="Description of the job.")
    required_skills: Optional[List[str]] = Field(None, description="Required skills for the job.")
    application_deadline: Optional[str] = Field(None, description="Deadline for job applications in DDMMYYYY format.")
    location: Optional[str] = Field(None, description="Location of the job.")
    salary: Optional[float] = Field(None, description="Salary for the job.")
    job_type: Optional[str] = Field(None, description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: Optional[bool] = Field(True, description="Status of the job, whether it is active or not.")
    file: Optional[UploadFile] = Field(None, description="File to upload with the job.")

class Update(BaseModel):
    job_id: int = Field(None, description="Unique identifier for the job.")
    title: Optional[str] = Field(None, description="Title of the job.")
    company: Optional[str] = Field(None, description="Company name.")
    description: Optional[str] = Field(None, description="Description of the job.")
    required_skills: Optional[List[str]] = Field(None, description="Required skills for the job.")
    application_deadline: Optional[str] = Field(None, description="Deadline for job applications in DDMMYYYY format.")
    location: Optional[str] = Field(None, description="Location of the job.")
    salary: Optional[float] = Field(None, description="Salary for the job.")
    job_type: Optional[str] = Field(None, description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: Optional[bool] = Field(None, description="Status of the job, whether it is active or not.")

class Get(BaseModel):
    job_id: Optional[int] = Field(None, description="Unique identifier for the job.")
    active: Optional[bool] = Field(None, description="Status of the job, whether it is active or not.")
    skills: Optional[List[str]] = Field(None, description="List of skills to filter by.")
