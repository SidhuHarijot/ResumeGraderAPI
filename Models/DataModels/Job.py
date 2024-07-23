from pydantic import BaseModel, Field, field_validator
from typing import List
from .Date import Date
from Errors.GetErrors import Errors as e
import regex as re

class Job(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    title: str = Field(..., description="Title of the job.")
    company: str = Field(..., description="Company name.")
    description: str = Field(..., description="Description of the job.")
    required_skills: List[str] = Field(..., description="Required skills for the job.")
    application_deadline: Date = Field(..., description="Deadline for job applications.")
    location: str = Field(..., description="Location of the job.")
    salary: float = Field(..., description="Salary for the job.")
    job_type: str = Field(..., description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: bool = Field(..., description="Status of the job, whether it is active or not.")

    @staticmethod
    def generate_default():
        return Job(
            job_id=-1,
            title="  ",
            company="  ",
            description="  ",
            required_skills=[],
            application_deadline=Date.create("00000000"),
            location="Unknown",
            salary=0.0,
            job_type="UNKN",
            active=True
        )

    @field_validator('job_id')
    def job_id_must_be_valid(cls, v):
        if v < -1:
            raise e.ContentInvalid.JobIdInvalid(v, "Job ID must be a positive integer")
        return v
    
    @field_validator('title')
    def title_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.TitleInvalid(v, "Title must be at least 2 characters long")
        if re.match(r'[;=]', v):
            raise e.ContentInvalid.TitleInvalid(v, "Title must contain only letters, numbers and spaces")
        return v
    
    @field_validator('company')
    def company_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.EmployerInvalid(v, "Company name must be at least 2 characters long")
        if re.match(r'[;=]', v):
            raise e.ContentInvalid.EmployerInvalid(v, "Company name must contain only letters, numbers and spaces")
        return v
    
    @field_validator('description')
    def description_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.DescriptionInvalid(v, "Description must be at least 2 characters long")
        if re.match(r'[;=]', v):
            raise e.ContentInvalid.DescriptionInvalid(v, "Description must contain only letters, numbers and spaces")
        return v
    
    @field_validator('required_skills')
    def required_skills_must_be_valid(cls, v):
        if not len(v) == 0:
            for skill in v:
                if re.match(r'[;=]', skill):
                    raise e.ContentInvalid.SkillsInvalid(v, f"Skill {skill} must contain only letters, numbers and spaces")
        return v
    
    @field_validator('application_deadline')
    def application_deadline_must_be_valid(cls, v):
        return v
    
    @field_validator('location')
    def location_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.LocationInvalid(v, "Location must be at least 2 characters long")
        if re.match(r'[;=]', v):
            raise e.ContentInvalid.LocationInvalid(v, "Location must contain only letters, numbers and spaces")
        return v
    
    @field_validator('salary')
    def salary_must_be_valid(cls, v):
        if v < 0.0:
            raise e.ContentInvalid.SalaryInvalid(v, "Salary must be a positive number")
        return v
    
    @field_validator('job_type')
    def job_type_must_be_valid(cls, v):
        if v not in ["FULL", "PART", "CONT", "UNKN"]:
            raise e.ContentInvalid.TypeInvalid(v, f"Job type {v} is invalid")
        return v
    
    @field_validator('active')
    def active_must_be_valid(cls, v):
        return v

    def __str__(self) -> str:
        return f"{self.title} at {self.company} in {self.location}. Salary: {self.salary}. Job type: {self.job_type}. Deadline: {str(self.application_deadline)}. Description: {self.description}. Required skills: {', '.join(self.required_skills)}. "

