from pydantic import BaseModel, Field, field_validator
from typing import List
from .Date import Date

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
            title="",
            company="",
            description="",
            required_skills=[],
            application_deadline=Date.create("00000000"),
            location="",
            salary=0.0,
            job_type="UNKN",
            active=True
        )


    def __str__(self) -> str:
        return f"{self.title} at {self.company} in {self.location}. Salary: {self.salary}. Job type: {self.job_type}. Deadline: {str(self.application_deadline)}. Description: {self.description}. Required skills: {', '.join(self.required_skills)}. "

