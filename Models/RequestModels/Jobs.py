from pydantic import BaseModel, Field
from fastapi import UploadFile, Query, File
from typing import List, Optional
from Models.DataModels.Job import Job
from Models.DataModels.Date import Date
 

class Create(BaseModel):
    title: Optional[str] = Field(default="", description="Title of the job.")
    company: Optional[str] = Field(default="", description="Company name.")
    description: Optional[str] = Field(default="", description="Description of the job.")
    required_skills: Optional[List[str]] = Field(default=[], description="Required skills for the job.")
    application_deadline: Optional[str] = Field(default="00000000", description="Deadline for job applications in DDMMYYYY format.")
    location: Optional[str] = Field(default="", description="Location of the job.")
    salary: Optional[float] = Field(default=0.0, description="Salary for the job.")
    job_type: Optional[str] = Field(default="UNKN", description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: Optional[bool] = Field(default=True, description="Status of the job, whether it is active or not.")
    auth_uid: str = Field(..., description="Unique identifier for the user.")

    def to_job(self):
        return Job(
            job_id=-1,
            title=self.title,
            company=self.company,
            description=self.description,
            required_skills=self.required_skills,
            application_deadline=Date.from_string(self.application_deadline),
            location=self.location,
            salary=self.salary,
            job_type=self.job_type,
            active=self.active
        )

class Update(BaseModel):
    job_id: int = Field(None, description="Unique identifier for the job.")
    auth_uid: str = Field(..., description="Unique identifier for the user.")
    title: Optional[str] = Field(None, description="Title of the job.")
    company: Optional[str] = Field(None, description="Company name.")
    description: Optional[str] = Field(None, description="Description of the job.")
    required_skills: Optional[List[str]] = Field(None, description="Required skills for the job.")
    application_deadline: Optional[str] = Field(None, description="Deadline for job applications in DDMMYYYY format.")
    location: Optional[str] = Field(None, description="Location of the job.")
    salary: Optional[float] = Field(None, description="Salary for the job.")
    job_type: Optional[str] = Field(None, description="Type of the job. Options: FULL, PART, CONT, UNKN")
    file: UploadFile = Field(File(None), description="File containing the job description.")
    active: Optional[bool] = Field(None, description="Status of the job, whether it is active or not.")

    def to_job(self, current: Job):
        if self.title:
            current.title = self.title
        if self.company:
            current.company = self.company
        if self.description:
            current.description = self.description
        if self.required_skills:
            current.required_skills = self.required_skills
        if self.application_deadline:
            current.application_deadline = Date.from_string(self.application_deadline)
        if self.location:
            current.location = self.location
        if self.salary:
            current.salary = self.salary
        if self.job_type:
            current.job_type = self.job_type
        if self.active is not None:
            current.active = self.active
        return current

class Get(BaseModel):
    active: Optional[bool] = Field(None, description="Status of the job, whether it is active or not.")
    skills: Optional[List[str]] = Field(None, description="List of skills to filter by.")
